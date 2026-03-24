# Dobby Immo

Immobilien-Management.

## Setup

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

## Project Structure

```
src/
  dobby_immo/       # Application code
    __init__.py
    main.py
tests/              # Test suite
  conftest.py
  test_main.py
```
