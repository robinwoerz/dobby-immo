"""Application settings loaded from environment / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env")

    telegram_bot_token: str
    telegram_bot_name: str
    telegram_allowed_user_ids: list[int] = []
