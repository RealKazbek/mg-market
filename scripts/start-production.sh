#!/usr/bin/env bash
set -euo pipefail

: "${PORT:=8000}"

required_vars=(
  BOT_TOKEN
  ADMIN_CHAT_ID
  ADMIN_PASSWORD
  ADMIN_TOKEN
  INTERNAL_SECRET
  MINIAPP_URL
  API_BASE_URL
  DATABASE_PATH
)

for name in "${required_vars[@]}"; do
  if [[ -z "${!name:-}" ]]; then
    echo "[startup] missing required environment variable: ${name}" >&2
    exit 1
  fi
done

mkdir -p "$(dirname -- "$DATABASE_PATH")"

backend_pid=""
bot_pid=""
stopping=0

cleanup() {
  stopping=1
  echo "[startup] stopping backend and bot"
  if [[ -n "$backend_pid" ]]; then kill "$backend_pid" 2>/dev/null || true; fi
  if [[ -n "$bot_pid" ]]; then kill "$bot_pid" 2>/dev/null || true; fi
  wait "$backend_pid" "$bot_pid" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

echo "[startup] starting FastAPI on 0.0.0.0:${PORT}"
(cd /app/backend && exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT") &
backend_pid=$!

echo "[startup] starting Telegram bot"
(cd /app/bot && exec python bot.py) &
bot_pid=$!

set +e
wait -n "$backend_pid" "$bot_pid"
status=$?
set -e

if [[ "$stopping" -eq 0 ]]; then
  echo "[startup] a critical process exited; stopping the container"
  exit "$status"
fi

exit 0
