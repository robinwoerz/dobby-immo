"""Telegram message handlers."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes

    from dobby_immo.agent import DobbyAgent

logger = logging.getLogger(__name__)


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Forward incoming message to the LLM agent and reply with its response."""
    if update.message is None or update.message.text is None:
        return

    agent: DobbyAgent = context.bot_data["agent"]
    chat_id = update.message.chat_id

    logger.info("Received: %s", update.message.text)
    reply = await agent.reply(chat_id, update.message.text)
    await update.message.reply_text(reply)


async def send_periodic_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a scheduled message to all allowed users."""
    user_ids: list[int] = context.bot_data["allowed_user_ids"]
    for user_id in user_ids:
        await context.bot.send_message(chat_id=user_id, text="Dobby meldet sich!")
