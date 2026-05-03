#!/usr/bin/env bash
set -euo pipefail

CLOUDFLARED="$HOME/.ai-home-control/bin/cloudflared"
if [[ ! -x "$CLOUDFLARED" ]]; then
  echo "cloudflared is not installed. Run ./ai_home_control/install_cloudflared.sh first." >&2
  exit 1
fi

echo "Starting Cloudflare Quick Tunnel for http://127.0.0.1:8787"
echo "Copy the https://*.trycloudflare.com URL printed below."
echo "Then run:"
echo "  ./ai_home_control/make_chatgpt_openapi.py https://YOUR-TUNNEL.trycloudflare.com"
exec "$CLOUDFLARED" tunnel --url http://127.0.0.1:8787
