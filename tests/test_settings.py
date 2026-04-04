"""Tests for application settings."""

from dobby_immo.settings import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "[111,222]")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    settings = Settings(_env_file=None)
    assert settings.telegram_bot_token == "fake-token"  # noqa: S105
    assert settings.telegram_allowed_user_ids == [111, 222]
    assert settings.openai_api_key == "sk-fake"
    assert settings.openai_chat_model == "gpt-5-mini"
    assert settings.openai_transcription_model == "gpt-4o-mini-transcribe"
    assert settings.openai_transcription_prompt is None
    assert settings.openai_tts_model == "gpt-4o-mini-tts"
    assert settings.openai_tts_voice == "fable"
    assert settings.openai_tts_speed == 1.2
    assert settings.profile_path == ".dobby/apartment_profile.md"
    assert settings.chat_history_max_messages == 30


def test_settings_transcription_overrides(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "[1]")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    monkeypatch.setenv("OPENAI_TRANSCRIPTION_MODEL", "whisper-1")
    monkeypatch.setenv("OPENAI_TRANSCRIPTION_PROMPT", "Immobilien Miete Kauf")
    settings = Settings(_env_file=None)
    assert settings.openai_transcription_model == "whisper-1"
    assert settings.openai_transcription_prompt == "Immobilien Miete Kauf"
