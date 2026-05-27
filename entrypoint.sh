#!/bin/sh
set -e

# Render injects $PORT at runtime; default to 8000 for local docker compose.
exec uv run uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
