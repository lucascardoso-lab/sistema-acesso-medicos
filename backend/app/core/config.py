from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "development"

    database_url: str

    secret_key: str
    access_token_expire_minutes: int = 480
    algorithm: str = "HS256"

    upload_dir: Path = Path("./uploads")
    max_upload_size: int = 5 * 1024 * 1024

    frontend_url: str = "http://localhost:5173"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def frontend_urls(self) -> list[str]:
        """FRONTEND_URL pode conter múltiplas origens separadas por vírgula
        (ex.: para liberar CORS também para o IP da máquina na rede local
        durante o desenvolvimento)."""
        return [url.strip() for url in self.frontend_url.split(",") if url.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
