#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$HOME/.ai-home-control"
TARGET_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$TARGET_DIR/com.local.ai-home-bridge.plist"

mkdir -p "$TARGET_DIR"
mkdir -p "$RUNTIME_DIR"
cp "$ROOT_DIR/ai_home_control/ha_ai_bridge.py" "$RUNTIME_DIR/ha_ai_bridge.py"
cp "$ROOT_DIR/ai_home_control/start_ai_home_bridge.sh" "$RUNTIME_DIR/start_ai_home_bridge.sh"
cp "$ROOT_DIR/ai_home_control/.env.example" "$RUNTIME_DIR/.env.example"
chmod +x "$RUNTIME_DIR/ha_ai_bridge.py" "$RUNTIME_DIR/start_ai_home_bridge.sh"

cat > "$TARGET_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.local.ai-home-bridge</string>
  <key>ProgramArguments</key>
  <array>
    <string>$RUNTIME_DIR/start_ai_home_bridge.sh</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/ai-home-bridge.out.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/ai-home-bridge.err.log</string>
  <key>WorkingDirectory</key>
  <string>$RUNTIME_DIR</string>
</dict>
</plist>
PLIST

launchctl unload "$TARGET_PLIST" 2>/dev/null || true
launchctl load "$TARGET_PLIST"

echo "AI Home Control bridge installed."
echo "Endpoint: http://127.0.0.1:8787"
echo "Runtime: $RUNTIME_DIR"
echo "Logs: /tmp/ai-home-bridge.out.log and /tmp/ai-home-bridge.err.log"
