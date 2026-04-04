# Project Instructions

## Project Overview

**dobby-immo** is a German-speaking Telegram bot for apartment search assistance.
The bot persona is "Dobby der freie Hauself" — enthusiastic, loyal, speaks in third person.
Users interact via text or voice messages; Dobby maintains a markdown-based apartment search profile on disk.

## Tech Stack

- **Python 3.12+** with strict mypy typing
- **uv** for dependency management, **Hatchling** as build backend
- **python-telegram-bot** (polling mode, not webhook)
- **OpenAI API**: Responses API (chat + tool calling), Audio Transcriptions (STT), Speech (TTS)
- **pydantic-settings** for env-based configuration
- **ffmpeg** (external binary) for OGG-to-WAV audio fallback conversion

## Project Structure

```
src/dobby_immo/
├── main.py              # CLI entry point, logging, app bootstrap
├── settings.py          # Env-backed config (pydantic-settings)
├── protocols.py         # Service protocols, Services container, AgentReply
├── agent/
│   ├── core.py          # DobbyAgent: OpenAI Responses API loop with tool execution
│   ├── tools.py         # @agent_tool decorator, tool registry + JSON schema generation
│   ├── profile.py       # ProfileStore: read/write apartment profile (markdown file)
│   ├── history.py       # ChatHistory: per-chat rolling deque
│   └── prompts.py       # German system prompt (Dobby persona)
├── telegram/
│   ├── bot.py           # create_app(): wires Services into bot_data, registers handlers
│   └── handlers.py      # Text/voice message handlers, TTS reply fallback
└── voice/
    ├── handler.py       # Voice download, size guard, transcribe -> agent -> reply
    ├── transcription.py # OpenAI transcriptions with ffmpeg retry on format errors
    ├── speech.py        # OpenAI TTS -> Opus bytes
    └── audio_convert.py # ffmpeg OGG->WAV conversion
tests/                   # Mirrors src/ structure; pytest + pytest-asyncio
```

## Architecture

```
Telegram (Text/Voice) -> Handler -> DobbyAgent (OpenAI Responses API + Tools) -> AgentReply -> Text or Voice response
```

- **Protocol-based DI**: Service interfaces defined as `Protocol` classes in `protocols.py`
- **Services container**: Frozen dataclass wired in `bot.py` via `bot_data[SERVICES_KEY]`
- **Multi-turn**: Agent uses `previous_response_id` for conversation continuity
- **Tool calling**: `speak_reply`, `read_apartment_profile`, `update_apartment_profile`
- **No database**: Profile = markdown file (default `.dobby/apartment_profile.md`), History = in-memory deque (lost on restart)
- **Security**: Telegram user-ID allowlist; bot refuses to start without it

## Configuration

See `.env.example` for all variables. Required:
- `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, `TELEGRAM_ALLOWED_USER_IDS` (JSON list)

Notable defaults: `openai_chat_model=gpt-5-mini`, `chat_history_max_messages=30`, `profile_path=.dobby/apartment_profile.md`

## Code Style

- ruff for linting and formatting (`line-length = 99`, `target-version = py312`)
- Google docstring style for public functions and classes
- No boilerplate code. Develop clean code.

## Dependencies

- The project uses uv
- Use `uv add ...` to add new dependencies

## Testing

- `make check` runs lint + typecheck + test (the full quality gate)
- `make test` for pytest only, `make lint` for ruff, `make typecheck` for mypy
- Tests use mocked Services fixtures from `tests/conftest.py`

## Agent Self-Update Rule

- At the end of each session where structural changes were made (new modules, changed architecture, new patterns, new dependencies), review this file and update it if the information is outdated.
- Only add stable, useful information that helps future sessions be immediately productive.
- Do not add volatile details, implementation specifics, or information obvious from reading the code.
- If user instructs you to update this file or mentions a working style, update it.
