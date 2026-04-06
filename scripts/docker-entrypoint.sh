#!/bin/bash
set -e

# 根據環境變數決定要執行的指令
if [ "$FASTAPI_APP_ENVIRONMENT" = "prod" ]; then
    # Production 模式
    exec uv run fastapi run backend/main.py "$@"
else
    # Development 模式 (預設)
    exec uv run fastapi dev backend/main.py "$@" --host ${UVICORN_HOST} --port ${UVICORN_PORT}
fi