# AI Home Control Bridge

This is a lower-level reference for `ai_home_control/`. For the full Custom GPT setup, see [gpts-ai-control.md](gpts-ai-control.md).

The bridge exposes current Home Assistant BESTIN devices through a narrow allowlist. It can be used by local AI agents through CLI/HTTP, or by Custom GPTs through a protected HTTPS tunnel.

## Required Environment

Create a Home Assistant long-lived access token:

1. Open your Home Assistant profile.
2. Scroll to `Long-Lived Access Tokens`.
3. Create a token named `AI Home Control`.
4. Put it in `ai_home_control/.env`.

```bash
cp ai_home_control/.env.example ai_home_control/.env
```

Example:

```text
HASS_URL=http://localhost:8123
HASS_TOKEN=paste-home-assistant-long-lived-access-token-here
AI_HOME_BRIDGE_API_KEY=optional-api-key-for-public-tunnels
```

## CLI Usage

```bash
./ai_home_control/ha_ai_bridge.py devices
./ai_home_control/ha_ai_bridge.py actions
./ai_home_control/ha_ai_bridge.py run turn_light --json '{"name":"거실","state":"on"}'
./ai_home_control/ha_ai_bridge.py run set_heating_temperature --json '{"name":"안방","temperature":24}'
./ai_home_control/ha_ai_bridge.py run set_ventilation --json '{"state":"off"}'
./ai_home_control/ha_ai_bridge.py run call_elevator_down --json '{"confirm":true}'
./ai_home_control/ha_ai_bridge.py run close_gas_valve --json '{"confirm":true}'
```

## HTTP Usage

Start the local API:

```bash
./ai_home_control/ha_ai_bridge.py serve --host 127.0.0.1 --port 8787
```

Health:

```bash
curl http://127.0.0.1:8787/health
```

Light control:

```bash
curl -X POST http://127.0.0.1:8787/light \
  -H 'Content-Type: application/json' \
  -d '{"name":"거실","state":"off"}'
```

Non-light action:

```bash
curl -X POST http://127.0.0.1:8787/run \
  -H 'Content-Type: application/json' \
  -d '{"action":"set_ventilation","params":{"state":"off"}}'
```

## Safety Policy

- Gas valve is close-only.
- Elevator call requires `confirm=true`.
- Only listed BESTIN entities can be controlled.
- Arbitrary Home Assistant service access is intentionally not exposed.
