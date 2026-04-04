"""Tests for dobby_immo components."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from dobby_immo.handlers import handle_message, send_periodic_message
from dobby_immo.settings import Settings
from dobby_immo.voice import handle_voice


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("TELEGRAM_BOT_NAME", "test_bot")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "[111,222]")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    settings = Settings(_env_file=None)
    assert settings.telegram_bot_token == "fake-token"  # noqa: S105
    assert settings.telegram_bot_name == "test_bot"
    assert settings.telegram_allowed_user_ids == [111, 222]
    assert settings.openai_api_key == "sk-fake"
    assert settings.openai_transcription_model == "gpt-4o-mini-transcribe"
    assert settings.openai_transcription_prompt is None


def test_settings_transcription_overrides(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("TELEGRAM_BOT_NAME", "test_bot")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "[1]")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    monkeypatch.setenv("OPENAI_TRANSCRIPTION_MODEL", "whisper-1")
    monkeypatch.setenv("OPENAI_TRANSCRIPTION_PROMPT", "Immobilien Miete Kauf")
    settings = Settings(_env_file=None)
    assert settings.openai_transcription_model == "whisper-1"
    assert settings.openai_transcription_prompt == "Immobilien Miete Kauf"


@pytest.mark.asyncio
async def test_handle_message_replies():
    agent = AsyncMock()
    agent.reply.return_value = "Dobby hilft!"

    message = MagicMock()
    message.text = "Hi there"
    message.chat_id = 42
    message.reply_text = AsyncMock()

    update = MagicMock()
    update.message = message

    context = MagicMock()
    context.bot_data = {"agent": agent}

    await handle_message(update, context)
    agent.reply.assert_called_once_with(42, "Hi there")
    message.reply_text.assert_called_once_with("Dobby hilft!")


@pytest.mark.asyncio
async def test_handle_message_ignores_empty_update():
    update = MagicMock()
    update.message = None

    await handle_message(update, MagicMock())


@pytest.mark.asyncio
async def test_send_periodic_message():
    context = MagicMock()
    context.bot_data = {"allowed_user_ids": [111, 222]}
    context.bot.send_message = AsyncMock()

    await send_periodic_message(context)

    assert context.bot.send_message.call_count == 2
    context.bot.send_message.assert_any_call(chat_id=111, text="Dobby meldet sich!")
    context.bot.send_message.assert_any_call(chat_id=222, text="Dobby meldet sich!")


@pytest.mark.asyncio
async def test_handle_voice_transcribes_and_replies():
    agent = AsyncMock()
    agent.reply.return_value = "Dobby antwortet!"

    transcription = AsyncMock()
    transcription.transcribe.return_value = "Was kostet die Wohnung?"

    tg_file = MagicMock()
    tg_file.file_path = "voice/file_1.oga"
    tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"fake-ogg"))

    message = MagicMock()
    message.voice = MagicMock()
    message.voice.file_id = "fid"
    message.voice.file_size = 1024
    message.chat_id = 7
    message.reply_text = AsyncMock()

    update = MagicMock()
    update.message = message

    context = MagicMock()
    context.bot_data = {"agent": agent, "transcription": transcription}
    context.bot.get_file = AsyncMock(return_value=tg_file)

    await handle_voice(update, context)

    transcription.transcribe.assert_called_once()
    args, _ = transcription.transcribe.call_args
    assert args[0] == b"fake-ogg"
    assert args[1] == "file_1.oga"
    agent.reply.assert_called_once_with(7, "Was kostet die Wohnung?")
    message.reply_text.assert_called_once_with("Dobby antwortet!")


@pytest.mark.asyncio
async def test_handle_voice_skips_when_no_voice():
    update = MagicMock()
    update.message = MagicMock()
    update.message.voice = None

    context = MagicMock()
    context.bot_data = {"agent": AsyncMock(), "transcription": AsyncMock()}

    await handle_voice(update, context)
    context.bot.get_file.assert_not_called()


@pytest.mark.asyncio
async def test_handle_voice_rejects_oversized_file():
    message = MagicMock()
    message.voice = MagicMock()
    message.voice.file_id = "fid"
    message.voice.file_size = 30 * 1024 * 1024
    message.reply_text = AsyncMock()

    update = MagicMock()
    update.message = message

    context = MagicMock()
    context.bot_data = {"agent": AsyncMock(), "transcription": AsyncMock()}

    await handle_voice(update, context)
    message.reply_text.assert_called_once()
    context.bot.get_file.assert_not_called()


@pytest.mark.asyncio
async def test_handle_voice_empty_transcript():
    agent = AsyncMock()
    transcription = AsyncMock()
    transcription.transcribe.return_value = "   "

    tg_file = MagicMock()
    tg_file.file_path = "x.oga"
    tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"x"))

    message = MagicMock()
    message.voice = MagicMock()
    message.voice.file_id = "fid"
    message.voice.file_size = 10
    message.chat_id = 1
    message.reply_text = AsyncMock()

    update = MagicMock()
    update.message = message

    context = MagicMock()
    context.bot_data = {"agent": agent, "transcription": transcription}
    context.bot.get_file = AsyncMock(return_value=tg_file)

    await handle_voice(update, context)
    agent.reply.assert_not_called()
    message.reply_text.assert_called_once()
