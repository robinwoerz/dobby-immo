"""Tests for dobby_immo components."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from dobby_immo.handlers import handle_message, send_periodic_message
from dobby_immo.settings import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("TELEGRAM_BOT_NAME", "test_bot")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "[111,222]")
    settings = Settings(_env_file=None)
    assert settings.telegram_bot_token == "fake-token"  # noqa: S105
    assert settings.telegram_bot_name == "test_bot"
    assert settings.telegram_allowed_user_ids == [111, 222]


@pytest.mark.asyncio
async def test_handle_message_replies():
    message = MagicMock()
    message.text = "Hi there"
    message.reply_text = AsyncMock()

    update = MagicMock()
    update.message = message

    await handle_message(update, MagicMock())
    message.reply_text.assert_called_once_with("Hallo Robin")


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
