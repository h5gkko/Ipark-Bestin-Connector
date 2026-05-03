# GPTs And AI Control

Use this path after Home Assistant can already control BESTIN entities.

The AI bridge in `ai_home_control/` exposes a narrow allowlist in front of Home Assistant. This is safer than giving an AI arbitrary Home Assistant service access.

## What The Bridge Exposes

- `POST /light`: lighting only, marked non-consequential for GPT Actions.
- `POST /run`: non-light actions, marked consequential.
- `GET /health`: bridge health.

Supported actions include:

- Lights on/off.
- Heating on/off.
- Heating target temperature.
- Electric switch on/off.
- Ventilation on/off.
- Elevator status.
- Optional elevator down call.
- Gas valve close only.
- Allowlisted state reads.

The bridge does not expose arbitrary Home Assistant services, shell commands, add-ons, or YAML editing.

## Step 1. Edit The Allowlist

Open:

```text
ai_home_control/ha_ai_bridge.py
```

Adjust these maps to your own Home Assistant entity IDs:

```python
LIGHTS = {...}
HEATING = {...}
ELECTRIC = {...}
READ_ONLY = {...}
```

Do not add entities you would not want an AI or voice assistant to control.

## Step 2. Create A Home Assistant Token

In Home Assistant:

1. Open your user profile.
2. Create a Long-Lived Access Token.
3. Save it in a local `.env` file:

```bash
cp ai_home_control/.env.example ai_home_control/.env
```

Edit:

```text
HASS_URL=http://localhost:8123
HASS_TOKEN=paste-home-assistant-long-lived-access-token-here
AI_HOME_BRIDGE_API_KEY=optional-api-key-for-public-tunnels
```

Never commit `.env`.

## Step 3. Run Locally

```bash
./ai_home_control/ha_ai_bridge.py serve --host 127.0.0.1 --port 8787
```

Health check:

```bash
curl http://127.0.0.1:8787/health
```

With a bridge API key:

```bash
curl http://127.0.0.1:8787/health \
  -H "Authorization: Bearer YOUR_BRIDGE_KEY"
```

## Step 4. Install As A macOS LaunchAgent

```bash
./ai_home_control/install_launch_agent.sh
```

This copies the bridge runtime to:

```text
~/.ai-home-control
```

and starts:

```text
http://127.0.0.1:8787
```

## Step 5. Generate A GPT Action Key

```bash
./ai_home_control/generate_bridge_api_key.sh
```

This writes local secret files. Do not commit them.

## Step 6. Expose For Custom GPTs

ChatGPT cannot reach `127.0.0.1` on your Mac directly. You need a public HTTPS endpoint.

Temporary Cloudflare Quick Tunnel:

```bash
./ai_home_control/install_cloudflared.sh
./ai_home_control/start_chatgpt_tunnel.sh
```

Copy the `https://....trycloudflare.com` URL.

Generate a schema with that URL:

```bash
./ai_home_control/make_chatgpt_openapi.py https://YOUR-TUNNEL.trycloudflare.com
```

Paste the generated `ai_home_control/chatgpt_openapi.json` into GPT Builder Actions.

For permanent use, use a stable HTTPS hostname instead of a temporary Quick Tunnel URL.

## Custom GPT Settings

Name:

```text
AI Home
```

Description:

```text
우리집 IoT를 ChatGPT로 제어합니다. 조명, 난방, 환풍기, 전기, 엘리베이터, 가스밸브 상태 확인 및 제어를 지원합니다.
```

Instructions:

```text
너는 우리집 Home Assistant/BESTIN IoT 제어 전용 GPT다.

기본 원칙:
- 사용자가 집 IoT 제어를 요청하면 연결된 Actions를 사용해 실제 기기를 제어한다.
- 가능한 경우 짧고 명확하게 응답한다.
- 조명 제어는 사용자가 명령하면 추가 확인 없이 바로 실행한다.
- 조명을 제외한 난방, 전기, 환풍기, 엘리베이터, 가스밸브 관련 작업은 실행 전 사용자 확인이 필요하다.
- 특히 엘리베이터 호출과 가스밸브 닫기는 실제 생활/안전에 영향이 있으므로 사용자의 명시 요청 없이 실행하지 않는다.
- 가스밸브는 닫기만 지원한다. 열기 요청은 거절한다.
- 지원하지 않는 기기나 모호한 요청이면 먼저 확인 질문을 한다.
- 토큰, API 키, 인증정보, 내부 URL, 보안 설정은 사용자에게 노출하지 않는다.

조명 제어:
- “거실 불 켜줘”, “안방 조명 꺼줘” 같은 요청은 turnLight를 호출한다.
- “불 다 꺼줘”처럼 여러 조명을 말하면 지원 조명 전체에 대해 순차적으로 조명 액션을 실행한다.

비조명 제어:
- 난방 온도 설정, 난방 켜기/끄기, 전기 스위치, 환풍기, 엘리베이터 호출, 가스밸브 닫기, 상태 조회는 runHomeAction을 사용한다.
- close_gas_valve와 call_elevator_down은 params에 confirm=true를 포함해야 한다.
- 엘리베이터 호출은 아래 방향 호출이다.
- 엘리베이터 상태를 물으면 get_elevator_status를 사용한다.
```

Privacy policy URL:

```text
https://github.com/h5gkko/Ipark-Bestin-Connector/blob/main/PRIVACY.md
```

## Consequential Action Behavior

The OpenAPI schema intentionally separates lights:

```text
/light -> x-openai-isConsequential: false
/run   -> x-openai-isConsequential: true
```

This lets Custom GPTs run lighting commands without a confirmation prompt, while still asking before other home-control operations.

## More Details

See also:

[chatgpt-actions.md](chatgpt-actions.md)
