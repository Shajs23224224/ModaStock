import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db_base import Base
from app.inventory import register_movement
from app.models import (
    Color,
    InventoryBalance,
    InventoryMovement,
    Product,
    ProductVariant,
    Role,
    Size,
    User,
)
from app.schemas import MovementCreate


@pytest.fixture()
def postgres_engine():
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is required for PostgreSQL integration tests")
    engine = create_engine(database_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_postgresql_readiness_and_schema_round_trip(postgres_engine):
    from fastapi.testclient import TestClient

    from app.db_session import get_db
    from app.main import app

    factory = sessionmaker(bind=postgres_engine, expire_on_commit=False)

    def override_get_db():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ready",
            "service": "modastock-api",
            "database": "ok",
        }
        assert postgres_engine.dialect.name == "postgresql"
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_postgresql_concurrent_sales_cannot_create_negative_stock(postgres_engine):
    factory = sessionmaker(bind=postgres_engine, expire_on_commit=False)
    with factory() as setup:
        role = Role(name="STAFF")
        setup.add(role)
        setup.flush()
        user = User(
            role_id=role.id,
            email="concurrency-staff@example.com",
            password_hash="test-only",
            full_name="Concurrency Test",
        )
        product = Product(name="Concurrent shirt", model_reference="CONC-001")
        size = Size(name="M-CONC")
        color = Color(name="Blue-CONC", hex_code="#0000FF")
        setup.add_all([user, product, size, color])
        setup.flush()
        variant = ProductVariant(
            product_id=product.id,
            size_id=size.id,
            color_id=color.id,
            sku="CONC-001-M-BLUE",
        )
        setup.add(variant)
        setup.flush()
        balance = InventoryBalance(variant_id=variant.id, quantity=10)
        setup.add(balance)
        setup.commit()
        variant_id, user_id, balance_id = variant.id, user.id, balance.id

    barrier = Barrier(2)

    def sell(key):
        with factory() as session:
            barrier.wait(timeout=10)
            try:
                register_movement(
                    session,
                    MovementCreate(
                        variant_id=variant_id,
                        movement_type="OUT",
                        quantity=7,
                        reason="Concurrent sale",
                    ),
                    user_id,
                    key,
                )
                return "success"
            except HTTPException as error:
                assert error.status_code == 409
                return "insufficient_stock"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(sell, ["parallel-sale-1", "parallel-sale-2"]))

    assert outcomes.count("success") == 1
    assert outcomes.count("insufficient_stock") == 1
    with factory() as verify:
        final_balance = verify.get(InventoryBalance, balance_id)
        movements = verify.scalars(
            select(InventoryMovement).where(InventoryMovement.variant_id == variant_id)
        ).all()
        assert final_balance.quantity == 3
        assert len(movements) == 1
