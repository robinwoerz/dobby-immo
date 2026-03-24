.DEFAULT_GOAL := help

.PHONY: help install lint format test typecheck check clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (dev included)
	uv sync

lint: ## Run ruff linter
	uv run ruff check src tests

format: ## Format code with ruff
	uv run ruff format src tests
	uv run ruff check --fix src tests

test: ## Run tests with pytest
	uv run pytest

typecheck: ## Run mypy type checking
	uv run mypy src

check: lint typecheck test ## Run all checks (lint + typecheck + test)

clean: ## Remove build artifacts
	rm -rf dist build .eggs *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	rm -f .coverage
	rm -rf htmlcov
