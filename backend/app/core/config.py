from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "EduSync ERP API"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://edusync:edusync@db:5432/edusync"
    jwt_secret: str = "change-me-in-local-env"
    storage_dir: str = "./storage"
    cors_origins: list[str] = ["http://localhost:5173","http://localhost:8000" ]
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
