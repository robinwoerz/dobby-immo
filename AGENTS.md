# Project Instructions

## Code Style
- Use ruff as defined in pyproject.toml for formatting
- Use google docstring style for public functions and classes
- No boilerplate code. Develop clean code.

## Architecture
- Use Protocol-based service interfaces (see `protocols.py`)
- Wire dependencies via the typed `Services` container in `bot.py`

## Dependencies
- The project uses uv
- Use "uv add..." to add new dependencies

## Testing
- Use the Makefile for testing via "make check" to see if there are any issues with you generated code


## Updates
- If user instructs you to update this AGENTS.md file or mentions a working style then update it.
