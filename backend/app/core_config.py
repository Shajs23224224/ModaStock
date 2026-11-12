from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ModaStock API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://modastock:change-me@localhost:5432/modastock"
    cors_origins: str = "http://localhost:5173"
    jwt_secret_key: str = "DEV-ONLY-CHANGE-THIS-SECRET-KEY-32-CHARS"
    access_token_expire_minutes: int = 30
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def cors_origin_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings():
    return Settings()
