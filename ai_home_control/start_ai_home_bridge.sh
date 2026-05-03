#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/ha_ai_bridge.py" ]]; then
  BRIDGE_SCRIPT="$SCRIPT_DIR/ha_ai_bridge.py"
  BRIDGE_ENV="$SCRIPT_DIR/.env"
else
  ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
  BRIDGE_SCRIPT="$ROOT_DIR/ai_home_control/ha_ai_bridge.py"
  BRIDGE_ENV="$ROOT_DIR/ai_home_control/.env"
fi

if [[ -f "$HOME/.hermes/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$HOME/.hermes/.env"
  set +a
fi

if [[ -f "$BRIDGE_ENV" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$BRIDGE_ENV"
  set +a
fi

export HASS_URL="${HASS_URL:-http://localhost:8123}"

exec "$BRIDGE_SCRIPT" serve --host 127.0.0.1 --port "${AI_HOME_BRIDGE_PORT:-8787}"
