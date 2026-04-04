"""Entry point for dobby-immo."""

import logging

from dobby_immo.settings import Settings
from dobby_immo.telegram import create_app


def main() -> None:
    """Load settings and start the Telegram bot."""
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=logging.INFO,
    )
    settings = Settings()
    app = create_app(settings)
    app.run_polling()


if __name__ == "__main__":
    main()
