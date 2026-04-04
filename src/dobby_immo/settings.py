"""Application settings loaded from environment / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env")

    telegram_bot_token: str
    telegram_allowed_user_ids: list[int] = []
    openai_api_key: str
    openai_chat_model: str = "gpt-5-mini"
    openai_transcription_model: str = "gpt-4o-mini-transcribe"
    openai_transcription_prompt: str | None = None
    openai_tts_model: str = "gpt-4o-mini-tts"
    openai_tts_voice: str = "fable"
    openai_tts_speed: float = 1.2
