from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "SiO Catalyst Quantum Studio"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./storage/sio_studio.sqlite3"
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    storage_dir: Path = Field(default=Path("storage"))
    gaussian16_path: str | None = None

    @property
    def upload_dir(self) -> Path:
        path = self.storage_dir / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def report_dir(self) -> Path:
        path = self.storage_dir / "reports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
