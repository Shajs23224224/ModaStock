import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db_base import Base
from app.db_session import get_db
from app.main import app


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL is required for PostgreSQL integration tests",
)
def test_postgresql_readiness_and_schema_round_trip():
    engine = create_engine(os.environ["TEST_DATABASE_URL"], pool_pre_ping=True)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

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
        assert engine.dialect.name == "postgresql"
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(engine)
        engine.dispose()
