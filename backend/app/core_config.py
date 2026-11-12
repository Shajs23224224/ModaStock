from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ModaStock API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://modastock:change-me@localhost:5432/modastock"
    cors_origins: str = "http://localhost:5173"
    jwt_secret_key: str = "DEV-ONLY-CHANGE-THIS-SECRET-KEY-32-CHARS"
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_runtime_security(self):
        if len(self.jwt_secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY debe tener al menos 32 caracteres")
        if self.environment.lower() not in {"development", "test"} and self.jwt_secret_key.startswith("DEV-ONLY-"):
            raise ValueError("Debes configurar un JWT_SECRET_KEY seguro fuera de desarrollo")
        return self

    @property
    def cors_origin_list(self):
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings():
    return Settings()
