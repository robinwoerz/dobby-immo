"""Telegram message handlers."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from openai import OpenAIError

from dobby_immo.protocols import AgentReply, get_services

if TYPE_CHECKING:
    from dobby_immo.protocols import SpeechService
    from telegram import Message, Update
    from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def send_agent_reply(
    message: Message,
    speech: SpeechService,
    reply: AgentReply,
) -> None:
    """Deliver an ``AgentReply`` as voice or text message."""
    if reply.use_voice:
        try:
            audio = await speech.synthesize(reply.text)
            await message.reply_voice(voice=audio)
            return
        except OpenAIError:
            logger.exception("TTS failed; falling back to text")
    await message.reply_text(reply.text)


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Forward incoming text message to the LLM agent and reply."""
    if update.message is None or update.message.text is None:
        return

    services = get_services(context.bot_data)
    chat_id = update.message.chat_id

    logger.info("Received: %s", update.message.text)
    try:
        reply = await services.agent.reply(chat_id, update.message.text)
    except OpenAIError:
        logger.exception("LLM reply failed for chat %s", chat_id)
        await update.message.reply_text(
            "Dobby's Magie ist gerade gestoert — bitte spaeter noch einmal versuchen!"
        )
        return
    await send_agent_reply(update.message, services.speech, reply)
