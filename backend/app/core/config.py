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

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    frontend_url: str = "http://localhost:5173"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
