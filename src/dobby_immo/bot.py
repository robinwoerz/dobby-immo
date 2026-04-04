"""Telegram bot application setup."""

import logging

from telegram.ext import Application, MessageHandler, filters

from dobby_immo.agent import DobbyAgent
from dobby_immo.handlers import handle_message, send_periodic_message
from dobby_immo.settings import Settings
from dobby_immo.voice import (
    OpenAISpeechRepository,
    OpenAITranscriptionRepository,
    handle_voice,
)

logger = logging.getLogger(__name__)


def create_app(settings: Settings) -> Application:  # type: ignore[type-arg]
    """Build and configure the Telegram bot application."""
    app: Application = (  # type: ignore[type-arg]
        Application.builder().token(settings.telegram_bot_token).build()
    )

    user_filter = filters.User(user_id=settings.telegram_allowed_user_ids)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, handle_message))
    app.add_handler(MessageHandler(filters.VOICE & user_filter, handle_voice))

    app.bot_data["allowed_user_ids"] = settings.telegram_allowed_user_ids
    app.bot_data["agent"] = DobbyAgent(api_key=settings.openai_api_key)
    app.bot_data["transcription"] = OpenAITranscriptionRepository(
        api_key=settings.openai_api_key,
        model=settings.openai_transcription_model,
        prompt=settings.openai_transcription_prompt,
    )
    app.bot_data["speech"] = OpenAISpeechRepository(
        api_key=settings.openai_api_key,
        model=settings.openai_tts_model,
        voice=settings.openai_tts_voice,
        speed=settings.openai_tts_speed,
    )

    job_queue = app.job_queue
    if job_queue is not None:
        job_queue.run_repeating(send_periodic_message, interval=20, first=5)

    logger.info(
        "Allowlist active — %d user(s) permitted",
        len(settings.telegram_allowed_user_ids),
    )
    return app
