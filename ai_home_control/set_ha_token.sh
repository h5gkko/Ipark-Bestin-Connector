#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_ENV="$HOME/.hermes/.env"
BRIDGE_ENV="$ROOT_DIR/ai_home_control/.env"

mkdir -p "$(dirname "$HERMES_ENV")" "$ROOT_DIR/ai_home_control"

printf 'Home Assistant Long-Lived Access Token: '
stty -echo
IFS= read -r TOKEN
stty echo
printf '\n'

if [[ -z "$TOKEN" ]]; then
  echo "Token is empty. Nothing changed." >&2
  exit 1
fi

update_env() {
  local file="$1"
  local tmp
  tmp="$(mktemp)"
  touch "$file"
  grep -v '^HASS_URL=' "$file" | grep -v '^HASS_TOKEN=' > "$tmp" || true
  {
    cat "$tmp"
    echo "HASS_URL=http://localhost:8123"
    echo "HASS_TOKEN=$TOKEN"
  } > "$file"
  rm -f "$tmp"
  chmod 600 "$file"
}

update_env "$HERMES_ENV"
update_env "$BRIDGE_ENV"

echo "Configured HASS_URL and HASS_TOKEN for Hermes Agent and AI Home Control bridge."
