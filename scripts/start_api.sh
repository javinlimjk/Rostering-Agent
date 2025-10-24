#!/bin/bash
# Start FastAPI server

echo "Starting FastAPI server..."
cd "$(dirname "$0")/.."
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
