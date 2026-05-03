#!/usr/bin/env bash
set -euo pipefail

CLOUDFLARED="$HOME/.ai-home-control/bin/cloudflared"
if [[ ! -x "$CLOUDFLARED" ]]; then
  echo "cloudflared is not installed. Run ./ai_home_control/install_cloudflared.sh first." >&2
  exit 1
fi

TARGET_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$TARGET_DIR/com.local.ai-home-bridge-tunnel.plist"
mkdir -p "$TARGET_DIR"

cat > "$TARGET_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.local.ai-home-bridge-tunnel</string>
  <key>ProgramArguments</key>
  <array>
    <string>$CLOUDFLARED</string>
    <string>tunnel</string>
    <string>--no-autoupdate</string>
    <string>--url</string>
    <string>http://127.0.0.1:8787</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/ai-home-bridge-tunnel.out.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/ai-home-bridge-tunnel.err.log</string>
  <key>WorkingDirectory</key>
  <string>$HOME/.ai-home-control</string>
</dict>
</plist>
PLIST

launchctl unload "$TARGET_PLIST" 2>/dev/null || true
: > /tmp/ai-home-bridge-tunnel.out.log
: > /tmp/ai-home-bridge-tunnel.err.log
launchctl load "$TARGET_PLIST"

echo "ChatGPT tunnel LaunchAgent installed."
echo "Waiting for public URL..."
for _ in {1..30}; do
  URL="$(grep -Eo 'https://[-a-zA-Z0-9.]+\.trycloudflare\.com' /tmp/ai-home-bridge-tunnel.err.log /tmp/ai-home-bridge-tunnel.out.log 2>/dev/null | head -n 1 || true)"
  if [[ -n "$URL" ]]; then
    echo "$URL"
    exit 0
  fi
  sleep 1
done

echo "Tunnel started, but URL was not detected yet." >&2
echo "Check: /tmp/ai-home-bridge-tunnel.err.log" >&2
exit 2
