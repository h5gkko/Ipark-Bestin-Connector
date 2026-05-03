#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="$HOME/.ai-home-control/bin"
mkdir -p "$INSTALL_DIR"

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.tgz"

echo "Downloading cloudflared for macOS Apple Silicon..."
curl -L "$URL" -o "$TMP_DIR/cloudflared.tgz"

tar -xzf "$TMP_DIR/cloudflared.tgz" -C "$TMP_DIR"
if [[ -f "$TMP_DIR/cloudflared" ]]; then
  cp "$TMP_DIR/cloudflared" "$INSTALL_DIR/cloudflared"
else
  FOUND="$(find "$TMP_DIR" -type f -name 'cloudflared' | head -n 1)"
  cp "$FOUND" "$INSTALL_DIR/cloudflared"
fi

chmod +x "$INSTALL_DIR/cloudflared"
"$INSTALL_DIR/cloudflared" --version
echo "Installed: $INSTALL_DIR/cloudflared"
