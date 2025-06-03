.PHONY: help restore

# Simple helper for setting up the development environment
help:
	@echo "Usage: make restore"
	@echo "  restore - Create .venv with uv and install dependencies"

restore:
	@test -d .venv || uv venv .venv
	@.venv/bin/uv pip install -r requirements.txt
