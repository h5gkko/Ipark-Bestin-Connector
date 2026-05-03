#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KEY="$("$ROOT_DIR/ai_home_control/ha_ai_bridge.py" __generate_key 2>/dev/null || python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
)"
FILES=(
  "$HOME/.hermes/.env"
  "$HOME/.ai-home-control/.env"
  "$ROOT_DIR/ai_home_control/.env"
)

write_key() {
  local file="$1"
  local tmp
  mkdir -p "$(dirname "$file")"
  touch "$file"
  tmp="$(mktemp)"
  grep -v '^AI_HOME_BRIDGE_API_KEY=' "$file" > "$tmp" || true
  {
    cat "$tmp"
    echo "AI_HOME_BRIDGE_API_KEY=$KEY"
  } > "$file"
  chmod 600 "$file"
  rm -f "$tmp"
}

for file in "${FILES[@]}"; do
  write_key "$file"
done

SECRET_FILE="$ROOT_DIR/ai_home_control/chatgpt_action_secret.txt"
{
  echo "ChatGPT Action authentication"
  echo "Authentication type: API Key"
  echo "Auth type: Bearer"
  echo "API key:"
  echo "$KEY"
} > "$SECRET_FILE"
chmod 600 "$SECRET_FILE"

echo "Generated AI_HOME_BRIDGE_API_KEY."
echo "Secret file: $SECRET_FILE"
echo "Restart the bridge after changing the key."
