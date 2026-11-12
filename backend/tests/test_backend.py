import uuid

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import get_current_user
from app.db_base import Base
from app.db_session import get_db
from app.inventory import register_movement
from app.main import app
from app.models import Color, InventoryBalance, Product, ProductVariant, Role, Size, User
from app.schemas import MovementCreate
from app.security import create_access_token


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def users(db):
    admin_role = Role(name="ADMIN")
    staff_role = Role(name="STAFF")
    db.add_all([admin_role, staff_role])
    db.flush()
    admin = User(
        role_id=admin_role.id,
        email="admin@example.com",
        password_hash="test-only",
        full_name="Admin Test",
    )
    staff = User(
        role_id=staff_role.id,
        email="staff@example.com",
        password_hash="test-only",
        full_name="Staff Test",
    )
    db.add_all([admin, staff])
    db.commit()
    return {
        "admin": admin,
        "staff": staff,
        "admin_headers": {"Authorization": f"Bearer {create_access_token(str(admin.id), 'ADMIN')}"},
        "staff_headers": {"Authorization": f"Bearer {create_access_token(str(staff.id), 'STAFF')}"},
    }


@pytest.fixture()
def client(db):
    def override():
        yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_products_require_auth_and_reject_duplicate_reference(client, users):
    payload = {"name": "Camiseta", "model_reference": "CAM-001"}
    assert client.post("/api/v1/products", json=payload).status_code == 401
    created = client.post("/api/v1/products", json=payload, headers=users["admin_headers"])
    assert created.status_code == 201
    listed = client.get("/api/v1/products", headers=users["staff_headers"])
    assert listed.status_code == 200
    assert listed.json()[0]["name"] == "Camiseta"
    duplicate = client.post("/api/v1/products", json=payload, headers=users["admin_headers"])
    assert duplicate.status_code == 409


def test_variant_initializes_balance_and_requires_manager_role(client, db, users):
    product = Product(name="Pantalón", model_reference="PAN-01")
    size = Size(name="M")
    color = Color(name="Negro", hex_code="#000000")
    db.add_all([product, size, color])
    db.commit()
    payload = {
        "size_id": str(size.id),
        "color_id": str(color.id),
        "sku": "PAN-M-NEG",
        "minimum_quantity": 2,
    }
    denied = client.post(
        f"/api/v1/products/{product.id}/variants",
        json=payload,
        headers=users["staff_headers"],
    )
    assert denied.status_code == 403
    created = client.post(
        f"/api/v1/products/{product.id}/variants",
        json=payload,
        headers=users["admin_headers"],
    )
    assert created.status_code == 201
    stock = client.get(
        f"/api/v1/variants/{created.json()['id']}/stock",
        headers=users["staff_headers"],
    )
    assert stock.status_code == 200
    assert stock.json()["quantity"] == 0
    assert stock.json()["minimum_quantity"] == 2


def test_movement_route_requires_authentication(client):
    assert client.post("/api/v1/inventory/movements", json={}).status_code == 401


def test_movement_service_and_rollback(db, users):
    user = users["staff"]
    product = Product(name="Camisa", model_reference="CAM-02")
    size = Size(name="L")
    color = Color(name="Azul", hex_code="#0000FF")
    db.add_all([product, size, color])
    db.flush()
    variant = ProductVariant(
        product_id=product.id,
        size_id=size.id,
        color_id=color.id,
        sku="CAM-L-AZU",
    )
    db.add(variant)
    db.flush()
    balance = InventoryBalance(variant_id=variant.id, quantity=0)
    db.add(balance)
    db.commit()

    incoming = MovementCreate(
        variant_id=variant.id, movement_type="IN", quantity=8, reason="Compra"
    )
    first = register_movement(db, incoming, user.id, "in-001")
    outgoing = MovementCreate(
        variant_id=variant.id, movement_type="OUT", quantity=3, reason="Venta"
    )
    second = register_movement(db, outgoing, user.id, "out-001")

    assert (first.stock_before, first.stock_after) == (0, 8)
    assert (second.stock_before, second.stock_after) == (8, 5)
    assert db.get(InventoryBalance, balance.id).quantity == 5

    with pytest.raises(HTTPException) as error:
        register_movement(
            db,
            MovementCreate(
                variant_id=variant.id,
                movement_type="OUT",
                quantity=99,
                reason="Venta",
            ),
            user.id,
        )
    assert error.value.status_code == 409
    assert db.get(InventoryBalance, balance.id).quantity == 5


def test_idempotent_retry_returns_original_movement(db, users):
    user = users["staff"]
    product = Product(name="Falda", model_reference="FAL-01")
    size = Size(name="S")
    color = Color(name="Rojo", hex_code="#FF0000")
    db.add_all([product, size, color])
    db.flush()
    variant = ProductVariant(
        product_id=product.id, size_id=size.id, color_id=color.id, sku="FAL-S-ROJ"
    )
    db.add(variant)
    db.flush()
    db.add(InventoryBalance(variant_id=variant.id, quantity=0))
    db.commit()

    payload = MovementCreate(
        variant_id=variant.id, movement_type="IN", quantity=5, reason="Compra"
    )
    first = register_movement(db, payload, user.id, "retry-001")
    retry = register_movement(db, payload, user.id, "retry-001")
    assert retry.id == first.id
    assert db.query(InventoryBalance).filter_by(variant_id=variant.id).one().quantity == 5
