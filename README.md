# Dobby Immo

Immobilien-Management.

## Setup

Voice memos are transcribed with the OpenAI Audio API. If the API rejects Telegram's OGG/Opus file, the bot runs **ffmpeg** once to convert to WAV — install ffmpeg on the host (e.g. `brew install ffmpeg` on macOS).

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
make install

# Install pre-commit hooks
uv run pre-commit install
```

## Development

```bash
make check      # Run all checks (lint + typecheck + test)
make lint        # Ruff linter
make format      # Auto-format code
make test        # Run tests
make typecheck   # mypy
```
