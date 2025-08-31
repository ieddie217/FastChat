# app/core/config.py
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict  # <-- v2 style

class Settings(BaseSettings):
    # Azure OpenAI
    DEBUG_AUDIT: bool = False

    ENDPOINT: str
    KEY: str
    API_VERSION: str = "2024-12-01-preview"
    DEPLOYMENT: str = "gpt-5-chat"

    # JWT
    JWT_SECRET: str = "change-me"
    JWT_ALG: str = "HS256"
    JWT_EXPIRE_MIN: int = 600
    # API meta
    API_TITLE: str = "AI Chat API"
    API_VERSION_STR: str = "1.0.0"
    API_DESCRIPTION: str = "Backend for chat"
    ALLOWED_ORIGINS: str = ""  # comma-separated list

    # pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # ignore unknown envs instead of erroring
    )

settings = Settings()

def allowed_origins() -> List[str]:
    if not settings.ALLOWED_ORIGINS:
        return []
    return [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
