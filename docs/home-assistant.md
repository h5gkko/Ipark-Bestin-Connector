# Home Assistant Setup

Use this path after IPARK/BESTIN UUID registration succeeds.

## Overview

Home Assistant talks to BESTIN through a custom integration. This repository does not vendor or redistribute that integration. Install the BESTIN custom integration separately, then use the UUID registered by [ipark-bestin-registration.md](ipark-bestin-registration.md).

## Recommended Order

1. Install Home Assistant.
2. Install the BESTIN custom integration.
3. Add the `BESTIN` integration.
4. Select `version2.0`.
5. Paste the registered UUID.
6. Verify discovered devices and entities.
7. Rename entities and assign areas.
8. Only then expose selected entities to Google Home or GPTs.

## Docker Example

On macOS with Docker Desktop:

```bash
docker run -d \
  --name homeassistant \
  --restart unless-stopped \
  -e TZ=Asia/Seoul \
  -p 8123:8123 \
  -v "$HOME/homeassistant:/config" \
  ghcr.io/home-assistant/home-assistant:stable
```

Open:

```text
http://localhost:8123
```

Check status:

```bash
docker ps
```

## BESTIN Integration

In Home Assistant:

1. Go to `Settings > Devices & services`.
2. Add integration.
3. Search for `BESTIN`.
4. Choose `version2.0`.
5. Enter the registered UUID.

Depending on your building and wallpad, optional fields such as elevator count or elevator/wallpad address may be needed.

## Entities To Verify

Common BESTIN entities may include:

- Smart lights
- Heating / thermostat
- Ventilation
- Electric and standby-cut switches
- Gas valve
- Indoor air sensors
- Elevator call and elevator floor/direction sensors

Availability varies by apartment, wallpad firmware, and custom integration support.

## Naming And Areas

After discovery, clean up entities before voice or AI exposure.

Suggested area mapping:

```text
1 -> 거실
2 -> 안방
3 -> 서재
4 -> 작은방
```

Useful grouping:

- Put gas valve in `주방`.
- Put ventilation and elevator entities in `공용부`.
- Keep the light device grouped if you prefer one BESTIN light device, while assigning each light entity to its real area.

Entity names and Home Assistant areas do not need to match exactly. Areas are mostly for dashboards, voice assistants, and grouping.

## Elevator Notes

Some wallpads only show elevator floor while an elevator call or movement is active. In that case Home Assistant may only update the current floor during a call/movement event, then keep the last known floor afterward.

Elevator calls affect a real shared building system. Expose them carefully.

## Gas Valve Safety

For safety, expose gas valve close only. Do not expose gas opening to AI or voice assistants.

## Google Home

Free options are possible but require your Home Assistant to be reachable over HTTPS:

- Home Assistant Cloud / Nabu Casa is the easiest, but paid.
- Manual Google Assistant integration can be free, but requires HTTPS, Google Cloud setup, and more configuration.
- Cloudflare Tunnel or another reverse proxy can provide HTTPS, but use a stable hostname and secure access.

Expose only selected entities first: lights, climate, fan, and safe switches.
