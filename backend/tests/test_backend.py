import uuid

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db_base import Base
from app.db_session import get_db
from app.inventory import register_movement
from app.main import app
from app.models import Color, InventoryBalance, Product, ProductVariant, Role, Size, User
from app.schemas import MovementCreate
from app.security import create_access_token, verify_password


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


def create_variant(db, suffix="001", quantity=0):
    product = Product(name=f"Camisa {suffix}", model_reference=f"CAM-{suffix}")
    size = Size(name=f"M-{suffix}")
    color = Color(name=f"Azul-{suffix}", hex_code="#0000FF")
    db.add_all([product, size, color])
    db.flush()
    variant = ProductVariant(
        product_id=product.id,
        size_id=size.id,
        color_id=color.id,
        sku=f"CAM-{suffix}-M-AZU",
    )
    db.add(variant)
    db.flush()
    balance = InventoryBalance(variant_id=variant.id, quantity=quantity)
    db.add(balance)
    db.commit()
    return variant, balance


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_registration_assigns_staff_and_login_returns_usable_token(client, db, users):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Usuario de prueba",
            "email": "new-user@example.com",
            "password": "password-test-2026",
        },
    )
    assert response.status_code == 201
    created = db.query(User).filter_by(email="new-user@example.com").one()
    assert db.get(Role, created.role_id).name == "STAFF"
    assert verify_password("password-test-2026", created.password_hash)

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "new-user@example.com", "password": "password-test-2026"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    profile = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )
    assert profile.status_code == 200
    assert profile.json()["role"] == "STAFF"


def test_invalid_credentials_and_invalid_token_are_rejected(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "wrong-password"},
    )
    assert login.status_code == 401
    profile = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )
    assert profile.status_code == 401


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


def test_authenticated_staff_can_register_idempotent_movement_through_api(client, db, users):
    variant, balance = create_variant(db, "API-001", quantity=4)
    payload = {
        "variant_id": str(variant.id),
        "movement_type": "IN",
        "quantity": 3,
        "reason": "Recepción de mercancía",
    }
    headers = {
        **users["staff_headers"],
        "Idempotency-Key": "api-movement-001",
    }
    first = client.post("/api/v1/inventory/movements", json=payload, headers=headers)
    retry = client.post("/api/v1/inventory/movements", json=payload, headers=headers)

    assert first.status_code == 201
    assert retry.status_code == 201
    assert retry.json()["id"] == first.json()["id"]
    db.refresh(balance)
    assert balance.quantity == 7


def test_movement_service_prevents_negative_stock_and_rolls_back(db, users):
    variant, balance = create_variant(db, "002", quantity=8)
    incoming = MovementCreate(
        variant_id=variant.id, movement_type="OUT", quantity=3, reason="Venta"
    )
    movement = register_movement(db, incoming, users["staff"].id, "out-001")
    assert (movement.stock_before, movement.stock_after) == (8, 5)

    with pytest.raises(HTTPException) as error:
        register_movement(
            db,
            MovementCreate(
                variant_id=variant.id,
                movement_type="OUT",
                quantity=99,
                reason="Venta",
            ),
            users["staff"].id,
        )
    assert error.value.status_code == 409
    db.refresh(balance)
    assert balance.quantity == 5


def test_idempotent_retry_returns_original_movement(db, users):
    variant, balance = create_variant(db, "003")
    payload = MovementCreate(
        variant_id=variant.id, movement_type="IN", quantity=5, reason="Compra"
    )
    first = register_movement(db, payload, users["staff"].id, "retry-001")
    retry = register_movement(db, payload, users["staff"].id, "retry-001")
    assert retry.id == first.id
    db.refresh(balance)
    assert balance.quantity == 5


def test_idempotency_key_cannot_be_reused_for_a_different_operation(db, users):
    variant, balance = create_variant(db, "004")
    original = MovementCreate(
        variant_id=variant.id, movement_type="IN", quantity=5, reason="Compra"
    )
    register_movement(db, original, users["staff"].id, "same-key")
    changed = MovementCreate(
        variant_id=variant.id, movement_type="IN", quantity=6, reason="Compra"
    )
    with pytest.raises(HTTPException) as error:
        register_movement(db, changed, users["staff"].id, "same-key")
    assert error.value.status_code == 409
    db.refresh(balance)
    assert balance.quantity == 5


def test_adjustment_increase_and_decrease_preserve_stock_ledger(db, users):
    variant, balance = create_variant(db, "005", quantity=10)
    increase = register_movement(
        db,
        MovementCreate(
            variant_id=variant.id,
            movement_type="ADJUSTMENT",
            adjustment_direction="INCREASE",
            quantity=2,
            reason="Conteo físico",
        ),
        users["staff"].id,
    )
    decrease = register_movement(
        db,
        MovementCreate(
            variant_id=variant.id,
            movement_type="ADJUSTMENT",
            adjustment_direction="DECREASE",
            quantity=3,
            reason="Corrección de conteo",
        ),
        users["staff"].id,
    )
    assert (increase.stock_before, increase.stock_after) == (10, 12)
    assert (decrease.stock_before, decrease.stock_after) == (12, 9)
    db.refresh(balance)
    assert balance.quantity == 9


def test_minimum_stock_update_requires_manager_and_rejects_negative(client, db, users):
    variant, _ = create_variant(db, "006")
    endpoint = f"/api/v1/variants/{variant.id}/minimum-stock"
    denied = client.patch(endpoint, json={"minimum_quantity": 4}, headers=users["staff_headers"])
    assert denied.status_code == 403
    invalid = client.patch(endpoint, json={"minimum_quantity": -1}, headers=users["admin_headers"])
    assert invalid.status_code == 422
    updated = client.patch(endpoint, json={"minimum_quantity": 4}, headers=users["admin_headers"])
    assert updated.status_code == 200
    assert updated.json()["minimum_quantity"] == 4
