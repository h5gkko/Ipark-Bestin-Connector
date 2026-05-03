# ChatGPT Actions Setup

ChatGPT cannot call `http://127.0.0.1` on your Mac directly. To use the bridge from a Custom GPT, expose the local bridge through a public HTTPS URL and protect it with a bearer key.

## 1. Confirm The Local Bridge Works

```bash
curl http://127.0.0.1:8787/health
```

If `AI_HOME_BRIDGE_API_KEY` is configured:

```bash
curl http://127.0.0.1:8787/health \
  -H "Authorization: Bearer YOUR_BRIDGE_KEY"
```

## 2. Generate A Bridge Key

```bash
./ai_home_control/generate_bridge_api_key.sh
```

This writes a local secret file:

```text
ai_home_control/chatgpt_action_secret.txt
```

Do not commit or share that file.

## 3. Start A Public HTTPS Tunnel

Install `cloudflared` locally:

```bash
./ai_home_control/install_cloudflared.sh
```

Start a temporary tunnel:

```bash
./ai_home_control/start_chatgpt_tunnel.sh
```

Copy the `https://....trycloudflare.com` URL.

For long-term use, prefer a stable Cloudflare Tunnel hostname or another HTTPS reverse proxy instead of a temporary Quick Tunnel URL.

## 4. Generate The OpenAPI Schema

```bash
./ai_home_control/make_chatgpt_openapi.py https://YOUR-TUNNEL.trycloudflare.com
```

This writes:

```text
ai_home_control/chatgpt_openapi.json
```

Paste that generated JSON into GPT Builder Actions.

## 5. Configure The Custom GPT Action

In GPT Builder:

1. Add an Action.
2. Authentication: `API Key`.
3. Auth type: `Bearer`.
4. API key: paste the key from `ai_home_control/chatgpt_action_secret.txt`.
5. Schema: paste `ai_home_control/chatgpt_openapi.json`.

## Action Design

The schema separates light control from other operations:

```text
POST /light -> turnLight, non-consequential
POST /run   -> runHomeAction, consequential
```

This means lighting can run without a confirmation prompt, while non-light home control still asks for confirmation in ChatGPT.

## Safety Notes

- Do not expose the bridge without `AI_HOME_BRIDGE_API_KEY`.
- Do not publish your tunnel URL.
- Do not publish the generated GPT Action key.
- Gas valve control should remain close-only.
- Elevator calls affect a real shared building system.
