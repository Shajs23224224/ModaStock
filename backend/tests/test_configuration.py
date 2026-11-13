import pytest
from pydantic import ValidationError

from app.core_config import Settings


def test_production_rejects_development_jwt_secret():
    with pytest.raises(ValidationError, match="JWT_SECRET_KEY seguro"):
        Settings(
            environment="production",
            jwt_secret_key="DEV-ONLY-CHANGE-THIS-SECRET-KEY-32-CHARS",
        )


def test_production_accepts_a_configured_secret():
    settings = Settings(
        environment="production",
        jwt_secret_key="production-secret-that-is-long-enough-123456",
    )
    assert settings.environment == "production"


def test_cors_origins_are_normalized():
    settings = Settings(cors_origins="https://app.example.com, http://localhost:5173 ")
    assert settings.cors_origin_list == [
        "https://app.example.com",
        "http://localhost:5173",
    ]
