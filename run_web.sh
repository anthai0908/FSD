#!/bin/sh
cd "$(dirname "$0")" || exit 1
(sleep 1; open http://127.0.0.1:8000/login) &
.venv-tk/bin/python WebApp.py
