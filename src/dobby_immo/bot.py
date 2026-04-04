"""Telegram bot application setup."""

import logging
from pathlib import Path

from telegram.ext import Application, MessageHandler, filters

from dobby_immo.agent import DobbyAgent
from dobby_immo.handlers import handle_message
from dobby_immo.protocols import SERVICES_KEY, Services
from dobby_immo.settings import Settings
from dobby_immo.voice import OpenAISpeechService, OpenAITranscriptionService, handle_voice

logger = logging.getLogger(__name__)


def create_app(settings: Settings) -> Application:  # type: ignore[type-arg]
    """Build and configure the Telegram bot application."""
    if not settings.telegram_allowed_user_ids:
        msg = "TELEGRAM_ALLOWED_USER_IDS is empty — refusing to start without an allowlist."
        raise SystemExit(msg)

    app: Application = (  # type: ignore[type-arg]
        Application.builder().token(settings.telegram_bot_token).build()
    )

    user_filter = filters.User(user_id=settings.telegram_allowed_user_ids)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, handle_message))
    app.add_handler(MessageHandler(filters.VOICE & user_filter, handle_voice))

    app.bot_data[SERVICES_KEY] = Services(
        agent=DobbyAgent(
            api_key=settings.openai_api_key,
            model=settings.openai_chat_model,
            profile_path=Path(settings.profile_path),
            max_history=settings.chat_history_max_messages,
        ),
        transcription=OpenAITranscriptionService(
            api_key=settings.openai_api_key,
            model=settings.openai_transcription_model,
            prompt=settings.openai_transcription_prompt,
        ),
        speech=OpenAISpeechService(
            api_key=settings.openai_api_key,
            model=settings.openai_tts_model,
            voice=settings.openai_tts_voice,
            speed=settings.openai_tts_speed,
        ),
    )

    logger.info(
        "Allowlist active — %d user(s) permitted",
        len(settings.telegram_allowed_user_ids),
    )
    return app
