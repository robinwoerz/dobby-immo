"""Telegram bot application setup."""

import logging

from telegram.ext import Application, MessageHandler, filters

from dobby_immo.agent import DobbyAgent
from dobby_immo.handlers import handle_message, send_periodic_message

logger = logging.getLogger(__name__)


def create_app(
    token: str,
    allowed_user_ids: list[int],
    openai_api_key: str,
) -> Application:  # type: ignore[type-arg]
    """Build and configure the Telegram bot application."""
    app: Application = Application.builder().token(token).build()  # type: ignore[type-arg]

    user_filter = filters.User(user_id=allowed_user_ids)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, handle_message))

    app.bot_data["allowed_user_ids"] = allowed_user_ids
    app.bot_data["agent"] = DobbyAgent(api_key=openai_api_key)

    job_queue = app.job_queue
    if job_queue is not None:
        job_queue.run_repeating(send_periodic_message, interval=20, first=5)

    logger.info("Allowlist active — %d user(s) permitted", len(allowed_user_ids))
    return app
