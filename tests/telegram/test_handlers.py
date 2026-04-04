"""Tests for Telegram message handlers."""

from unittest.mock import MagicMock

import pytest

from dobby_immo.protocols import AgentReply
from dobby_immo.telegram.handlers import handle_message


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
