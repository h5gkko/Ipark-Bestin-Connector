#!/usr/bin/env python3
"""Safe Home Assistant bridge for AI agents.

This exposes only the BESTIN entities we intentionally allow. It can be used as
a CLI by local agents or as a small localhost HTTP API by generic AI tools.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


DEFAULT_HASS_URL = "http://localhost:8123"

LIGHTS = {
    "거실": "light.bestin_smartlight_smartlight_1_1",
    "복도": "light.bestin_smartlight_smartlight_1_2",
    "싱크대": "light.bestin_smartlight_smartlight_2_1",
    "작은불": "light.bestin_smartlight_smartlight_2_2",
    "식탁": "light.bestin_smartlight_smartlight_2_3",
    "안방": "light.bestin_smartlight_smartlight_3_1",
    "서재": "light.bestin_smartlight_smartlight_4_1",
    "작은방": "light.bestin_smartlight_smartlight_5_1",
}

HEATING = {
    "거실": "climate.bestin_thermostat_thermostat_1",
    "안방": "climate.bestin_thermostat_thermostat_2",
    "서재": "climate.bestin_thermostat_thermostat_3",
    "작은방": "climate.bestin_thermostat_thermostat_4",
}

ELECTRIC = {
    "거실_1": "switch.bestin_electric_electric_1_1",
    "거실_2": "switch.bestin_electric_electric_1_2",
    "거실_대기전력_1": "switch.bestin_electric_electric_1_standbycut_1",
    "거실_대기전력_2": "switch.bestin_electric_electric_1_standbycut_2",
    "안방_1": "switch.bestin_electric_electric_2_1",
    "안방_2": "switch.bestin_electric_electric_2_2",
    "안방_대기전력_1": "switch.bestin_electric_electric_2_standbycut_1",
    "안방_대기전력_2": "switch.bestin_electric_electric_2_standbycut_2",
    "서재_1": "switch.bestin_electric_electric_3_1",
    "서재_2": "switch.bestin_electric_electric_3_2",
    "서재_대기전력_1": "switch.bestin_electric_electric_3_standbycut_1",
    "서재_대기전력_2": "switch.bestin_electric_electric_3_standbycut_2",
    "작은방_1": "switch.bestin_electric_electric_4_1",
    "작은방_2": "switch.bestin_electric_electric_4_2",
    "작은방_대기전력_1": "switch.bestin_electric_electric_4_standbycut_1",
    "작은방_대기전력_2": "switch.bestin_electric_electric_4_standbycut_2",
    "전기_5_1": "switch.bestin_electric_electric_5_1",
    "전기_5_2": "switch.bestin_electric_electric_5_2",
    "전기_5_대기전력_1": "switch.bestin_electric_electric_5_standbycut_1",
    "전기_5_대기전력_2": "switch.bestin_electric_electric_5_standbycut_2",
}

READ_ONLY = {
    "엘리베이터_현재층": "sensor.bestin_elevator_floor_1",
    "엘리베이터_방향": "sensor.bestin_elevator_direction_1",
}

CONTROL_ENTITIES = set(LIGHTS.values()) | set(HEATING.values()) | set(ELECTRIC.values()) | {
    "fan.bestin_ventil_1",
    "script.elevator_call_down",
    "switch.bestin_gas_valve",
}
READ_ENTITIES = CONTROL_ENTITIES | set(READ_ONLY.values())


class BridgeError(Exception):
    """A human-readable bridge error."""


def hass_url() -> str:
    return os.getenv("HASS_URL", DEFAULT_HASS_URL).rstrip("/")


def hass_token() -> str:
    return os.getenv("HASS_TOKEN", "")


def bridge_api_key() -> str:
    return os.getenv("AI_HOME_BRIDGE_API_KEY", "")


def check_bridge_auth(headers: Any) -> None:
    expected = bridge_api_key()
    if not expected:
        return

    auth = headers.get("Authorization", "")
    header_key = headers.get("X-Bridge-Key", "")
    supplied = ""
    if auth.startswith("Bearer "):
        supplied = auth.removeprefix("Bearer ").strip()
    elif header_key:
        supplied = header_key.strip()

    if supplied != expected:
        raise BridgeError("Unauthorized bridge request")


def ensure_token() -> str:
    token = hass_token()
    if not token:
        raise BridgeError(
            "HASS_TOKEN is not set. Create a Home Assistant long-lived access "
            "token from Profile > Long-Lived Access Tokens, then set HASS_TOKEN."
        )
    return token


def normalize_state(value: Any) -> str:
    state = str(value).lower()
    if state in {"on", "true", "1", "켜", "켜기", "open"}:
        return "on"
    if state in {"off", "false", "0", "꺼", "끄기", "close", "닫기"}:
        return "off"
    raise BridgeError("state must be one of: on, off")


def require_confirmation(params: dict[str, Any], action: str) -> None:
    if params.get("confirm") is not True:
        raise BridgeError(f"{action} requires confirm=true.")


def request_json(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    token = ensure_token()
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{hass_url()}{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise BridgeError(f"Home Assistant HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise BridgeError(f"Cannot reach Home Assistant at {hass_url()}: {exc}") from exc


def call_service(domain: str, service: str, entity_id: str, data: dict[str, Any] | None = None) -> Any:
    if entity_id not in CONTROL_ENTITIES:
        raise BridgeError(f"Entity is not allowed for control: {entity_id}")
    payload = dict(data or {})
    payload["entity_id"] = entity_id
    return request_json("POST", f"/api/services/{domain}/{service}", payload)


def get_state(entity_id: str) -> Any:
    if entity_id not in READ_ENTITIES:
        raise BridgeError(f"Entity is not allowed for reading: {entity_id}")
    quoted = urllib.parse.quote(entity_id, safe="")
    return request_json("GET", f"/api/states/{quoted}")


def available_actions() -> dict[str, Any]:
    return {
        "turn_light": {"params": {"name": sorted(LIGHTS), "state": ["on", "off"]}},
        "set_heating_temperature": {"params": {"name": sorted(HEATING), "temperature": "number"}},
        "turn_heating": {"params": {"name": sorted(HEATING), "state": ["on", "off"]}},
        "turn_electric": {"params": {"name": sorted(ELECTRIC), "state": ["on", "off"]}},
        "set_ventilation": {"params": {"state": ["on", "off"]}},
        "close_gas_valve": {"params": {"confirm": True}, "safety": "close only"},
        "call_elevator_down": {"params": {"confirm": True}, "safety": "calls real elevator"},
        "get_elevator_status": {"params": {}},
        "get_state": {"params": {"entity_id": sorted(READ_ENTITIES)}},
        "list_devices": {"params": {}},
    }


def run_action(action: str, params: dict[str, Any]) -> Any:
    if action == "list_devices":
        return {
            "lights": LIGHTS,
            "heating": HEATING,
            "electric": ELECTRIC,
            "fan": {"환풍기": "fan.bestin_ventil_1"},
            "gas": {"가스밸브_닫기만": "switch.bestin_gas_valve"},
            "elevator": {
                "호출": "script.elevator_call_down",
                "현재층": READ_ONLY["엘리베이터_현재층"],
                "방향": READ_ONLY["엘리베이터_방향"],
            },
        }

    if action == "turn_light":
        name = params.get("name")
        entity_id = LIGHTS.get(name)
        if not entity_id:
            raise BridgeError(f"Unknown light name: {name}")
        state = normalize_state(params.get("state"))
        return call_service("light", f"turn_{state}", entity_id)

    if action == "set_heating_temperature":
        name = params.get("name")
        entity_id = HEATING.get(name)
        if not entity_id:
            raise BridgeError(f"Unknown heating name: {name}")
        try:
            temperature = float(params["temperature"])
        except (KeyError, TypeError, ValueError) as exc:
            raise BridgeError("temperature must be a number") from exc
        if not 5 <= temperature <= 35:
            raise BridgeError("temperature must be between 5 and 35")
        return call_service(
            "climate",
            "set_temperature",
            entity_id,
            {"temperature": temperature, "hvac_mode": "heat"},
        )

    if action == "turn_heating":
        name = params.get("name")
        entity_id = HEATING.get(name)
        if not entity_id:
            raise BridgeError(f"Unknown heating name: {name}")
        state = normalize_state(params.get("state"))
        hvac_mode = "heat" if state == "on" else "off"
        return call_service("climate", "set_hvac_mode", entity_id, {"hvac_mode": hvac_mode})

    if action == "turn_electric":
        name = params.get("name")
        entity_id = ELECTRIC.get(name)
        if not entity_id:
            raise BridgeError(f"Unknown electric name: {name}")
        state = normalize_state(params.get("state"))
        return call_service("switch", f"turn_{state}", entity_id)

    if action == "set_ventilation":
        state = normalize_state(params.get("state"))
        return call_service("fan", f"turn_{state}", "fan.bestin_ventil_1")

    if action == "close_gas_valve":
        require_confirmation(params, action)
        return call_service("switch", "turn_off", "switch.bestin_gas_valve")

    if action == "call_elevator_down":
        require_confirmation(params, action)
        return call_service("script", "turn_on", "script.elevator_call_down")

    if action == "get_elevator_status":
        return {
            "floor": get_state(READ_ONLY["엘리베이터_현재층"]),
            "direction": get_state(READ_ONLY["엘리베이터_방향"]),
        }

    if action == "get_state":
        entity_id = params.get("entity_id")
        if not isinstance(entity_id, str):
            raise BridgeError("entity_id is required")
        return get_state(entity_id)

    raise BridgeError(f"Unknown action: {action}")


def result_ok(result: Any) -> dict[str, Any]:
    return {"ok": True, "result": result}


def result_error(error: Exception) -> dict[str, Any]:
    return {"ok": False, "error": str(error)}


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        try:
            check_bridge_auth(self.headers)
            if self.path == "/health":
                self._send(
                    200,
                    result_ok(
                        {
                            "hass_url": hass_url(),
                            "token_configured": bool(hass_token()),
                            "bridge_auth_required": bool(bridge_api_key()),
                        }
                    ),
                )
                return
            if self.path == "/actions":
                self._send(200, result_ok(available_actions()))
                return
            self._send(404, result_error(BridgeError("not found")))
        except Exception as exc:
            self._send(401, result_error(exc))

    def do_POST(self) -> None:
        try:
            check_bridge_auth(self.headers)
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            if not isinstance(payload, dict):
                raise BridgeError("POST body must be a JSON object")

            if self.path == "/light":
                self._send(200, result_ok(run_action("turn_light", payload)))
                return

            if self.path != "/run":
                self._send(404, result_error(BridgeError("not found")))
                return

            action = payload.get("action")
            params = payload.get("params") or {}
            if not isinstance(action, str) or not isinstance(params, dict):
                raise BridgeError("POST /run requires {'action': string, 'params': object}")
            if action == "turn_light":
                raise BridgeError("Use POST /light for light control.")
            self._send(200, result_ok(run_action(action, params)))
        except Exception as exc:
            self._send(400, result_error(exc))

    def log_message(self, format: str, *args: Any) -> None:
        sys.stderr.write("ha_ai_bridge: " + format % args + "\n")


def load_json_arg(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise BridgeError("--json must be a JSON object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe AI bridge for Home Assistant BESTIN control")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("actions", help="print available action schema")
    sub.add_parser("devices", help="print allowed device map")

    run_parser = sub.add_parser("run", help="run an allowlisted action")
    run_parser.add_argument("action")
    run_parser.add_argument("--json", default="{}", help="JSON object with action parameters")

    state_parser = sub.add_parser("state", help="read an allowlisted entity state")
    state_parser.add_argument("entity_id")

    serve_parser = sub.add_parser("serve", help="start localhost HTTP API")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8787)

    args = parser.parse_args()
    try:
        if args.command == "actions":
            print(json.dumps(result_ok(available_actions()), ensure_ascii=False, indent=2))
        elif args.command == "devices":
            print(json.dumps(result_ok(run_action("list_devices", {})), ensure_ascii=False, indent=2))
        elif args.command == "run":
            print(json.dumps(result_ok(run_action(args.action, load_json_arg(args.json))), ensure_ascii=False, indent=2))
        elif args.command == "state":
            print(json.dumps(result_ok(get_state(args.entity_id)), ensure_ascii=False, indent=2))
        elif args.command == "serve":
            server = ThreadingHTTPServer((args.host, args.port), Handler)
            print(f"Serving HA AI bridge on http://{args.host}:{args.port}", flush=True)
            server.serve_forever()
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(json.dumps(result_error(exc), ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
