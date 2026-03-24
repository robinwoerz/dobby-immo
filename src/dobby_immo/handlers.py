"""Telegram message handlers."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> None:
    """Log incoming message and reply with a greeting."""
    if update.message is None:
        return
    logger.info("Received: %s", update.message.text)
    await update.message.reply_text("Hallo Robin")


async def send_periodic_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a scheduled message to all allowed users."""
    user_ids: list[int] = context.bot_data["allowed_user_ids"]
    for user_id in user_ids:
        await context.bot.send_message(chat_id=user_id, text="Dobby meldet sich!")
