#!/bin/sh
cd "$(dirname "$0")" || exit 1
exec ./run_async_web.sh
