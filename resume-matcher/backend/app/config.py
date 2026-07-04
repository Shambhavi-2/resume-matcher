from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "sqlite:///./matcher.db"
    secret_key: str = "dev-secret-key-change-me"
    access_token_expire_minutes: int = 1440
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = ".env"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
