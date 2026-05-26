#!/bin/sh
cd "$(dirname "$0")" || exit 1
PORT=8001
(sleep 1; open "http://127.0.0.1:${PORT}/login") &
.venv-tk/bin/python -m uvicorn AsyncWebApp:app --host 127.0.0.1 --port "$PORT"
