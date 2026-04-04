"""Tests for Telegram message handlers."""

from unittest.mock import MagicMock

import pytest

from dobby_immo.handlers import handle_message, send_periodic_message
from dobby_immo.protocols import AgentReply


@pytest.mark.asyncio
async def test_handle_message_replies_text(update, context, agent):
    update.message.text = "Hi there"

    await handle_message(update, context)

    agent.reply.assert_called_once_with(42, "Hi there")
    update.message.reply_text.assert_called_once_with("Dobby hilft!")
    update.message.reply_voice.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_replies_voice(update, context, agent, speech):
    """When the agent returns use_voice=True, a voice message is sent."""
    update.message.text = "Antworte per Sprache"
    agent.reply.return_value = AgentReply(text="Dobby spricht!", use_voice=True)

    await handle_message(update, context)

    speech.synthesize.assert_called_once_with("Dobby spricht!")
    update.message.reply_voice.assert_called_once_with(voice=b"fake-opus")
    update.message.reply_text.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_ignores_empty_update(context):
    update = MagicMock()
    update.message = None

    await handle_message(update, context)


@pytest.mark.asyncio
async def test_send_periodic_message(context):
    await send_periodic_message(context)

    assert context.bot.send_message.call_count == 2
    context.bot.send_message.assert_any_call(chat_id=111, text="Dobby meldet sich!")
    context.bot.send_message.assert_any_call(chat_id=222, text="Dobby meldet sich!")
