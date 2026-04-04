"""Entry point for dobby-immo."""

import logging

from dobby_immo.bot import create_app
from dobby_immo.settings import Settings


def main() -> None:
    """Load settings and start the Telegram bot."""
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=logging.INFO,
    )
    settings = Settings()
    app = create_app(
        settings.telegram_bot_token,
        settings.telegram_allowed_user_ids,
        settings.openai_api_key,
        openai_transcription_model=settings.openai_transcription_model,
        openai_transcription_prompt=settings.openai_transcription_prompt,
    )
    app.run_polling()


if __name__ == "__main__":
    main()
