#!/bin/sh
cd "$(dirname "$0")" || exit 1
export TK_SILENCE_DEPRECATION=1
.venv-tk/bin/python GUI.py
