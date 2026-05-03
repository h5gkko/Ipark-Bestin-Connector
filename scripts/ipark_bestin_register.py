#!/usr/bin/env python3
"""Register IPARK/HDC Smart Home BESTIN mobile access for Home Assistant."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any


AUTH_BASE = "https://center.hdc-smart.com"
DEFAULT_ALIAS = "AI Assist"
DEFAULT_STATE = "/tmp/ipark-bestin-register-state.json"


class BestinError(Exception):
    """Human-readable registration error."""


def normalize_identifier(value: str | None, dong: str | None, ho: str | None) -> str:
    if value:
        compact = value.strip().replace(" ", "")
        compact = compact.replace("동", "/").replace("호", "")
        compact = re.sub(r"/+", "/", compact)
        compact = compact.strip("/")
        if "/" in compact:
            left, right = compact.split("/", 1)
            if left.isdigit() and right.isdigit():
                return f"{int(left)}/{int(right)}"
        raise BestinError("동/호는 101/1203 같은 형식이어야 합니다.")

    if not dong or not ho:
        raise BestinError("--identifier 또는 --dong/--ho를 입력해야 합니다.")
    if not dong.isdigit() or not ho.isdigit():
        raise BestinError("동과 호는 숫자여야 합니다.")
    return f"{int(dong)}/{int(ho)}"


def request_json(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    auth_uuid: str | None = None,
    timeout: int = 10,
) -> tuple[int, Any]:
    url = f"{AUTH_BASE}{path}"
    data = None
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }
    if auth_uuid:
        headers["Authorization"] = auth_uuid
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed: Any = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw
        return exc.code, parsed
    except urllib.error.URLError as exc:
        raise BestinError(f"네트워크 오류: {exc.reason}") from exc
    except TimeoutError as exc:
        raise BestinError("요청 시간이 초과되었습니다.") from exc


def iter_objects(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_objects(child)
    elif isinstance(value, list):
        for item in value:
            yield from iter_objects(item)


def pick_first(obj: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in obj and obj[key] not in (None, ""):
            return obj[key]
    return None


def resolve_site(args: argparse.Namespace) -> int:
    status, data = request_json("GET", "/v3/auth/valley")
    if status != 200:
        raise BestinError(f"단지 목록 조회 실패 HTTP {status}: {data}")

    query = args.query.strip().replace(" ", "").lower()
    matches: list[dict[str, Any]] = []
    for obj in iter_objects(data):
        name = pick_first(obj, ("name", "site_name", "valley_name", "apt_name", "complex_name"))
        code = pick_first(obj, ("code", "site", "site_code", "valley", "valley_code"))
        url = pick_first(obj, ("url", "server_url", "home_url"))
        if not name or not code:
            continue
        if query in str(name).replace(" ", "").lower():
            matches.append({"name": str(name), "code": str(code), "url": url})

    if not matches:
        raise BestinError("일치하는 단지를 찾지 못했습니다. 단지명을 줄여서 다시 검색해 보세요.")

    if len(matches) > 1 and not args.first:
        print("여러 단지가 검색되었습니다. 정확한 단지를 골라 --site-code로 사용하세요.")
        for item in matches:
            print(json.dumps(item, ensure_ascii=False))
        return 2

    item = matches[0]
    print(json.dumps(item, ensure_ascii=False, indent=2))
    print(f"\nsite-code: {item['code']}")
    return 0


def register(args: argparse.Namespace) -> int:
    identifier = normalize_identifier(args.identifier, args.dong, args.ho)
    auth_uuid = args.uuid or str(uuid.uuid4())
    body = {
        "site": str(args.site_code),
        "identifier": identifier,
        "alias": args.alias,
    }

    started = int(time.time())
    status, data = request_json(
        "POST",
        "/v3/auth/registration",
        body=body,
        auth_uuid=auth_uuid,
        timeout=8,
    )
    if status != 200:
        raise BestinError(f"등록 요청 실패 HTTP {status}: {data}")

    transaction = data.get("transaction") if isinstance(data, dict) else None
    if not transaction:
        raise BestinError(f"등록 요청은 응답했지만 transaction이 없습니다: {data}")

    state = {
        "uuid": auth_uuid,
        "site_code": str(args.site_code),
        "identifier": identifier,
        "alias": args.alias,
        "transaction": transaction,
        "started_at": started,
    }
    state_path = Path(args.state).expanduser()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    print("BESTIN 등록 요청을 보냈습니다.")
    print(f"등록 이름: {args.alias}")
    print(f"동/호: {identifier}")
    print(f"UUID: {auth_uuid}")
    print(f"state: {state_path}")
    print("월패드에 표시된 6자리 인증번호를 사용자에게 받아 verify를 실행하세요.")
    return 0


def verify(args: argparse.Namespace) -> int:
    state_path = Path(args.state).expanduser()
    if not state_path.exists():
        raise BestinError(f"state 파일이 없습니다: {state_path}")
    state = json.loads(state_path.read_text(encoding="utf-8"))

    code = args.code.strip()
    if not re.fullmatch(r"\d{6}", code):
        raise BestinError("인증번호는 6자리 숫자여야 합니다.")

    elapsed = int(time.time()) - int(state.get("started_at", time.time()))
    if elapsed > 180:
        print(f"주의: 등록 요청 후 {elapsed}초가 지났습니다. 월패드 인증이 만료됐을 수 있습니다.", file=sys.stderr)

    body = {
        "transaction": state["transaction"],
        "password": code,
    }
    status, data = request_json(
        "POST",
        "/v3/auth/verify",
        body=body,
        auth_uuid=state["uuid"],
        timeout=8,
    )
    if status != 200:
        raise BestinError(f"인증 실패 HTTP {status}: {data}")

    print("BESTIN 모바일 기기 등록이 완료되었습니다.")
    print(f"등록 이름: {state.get('alias', DEFAULT_ALIAS)}")
    print(f"Home Assistant BESTIN version2.0 UUID: {state['uuid']}")
    return 0


def login(args: argparse.Namespace) -> int:
    status, data = request_json(
        "POST",
        "/v3/auth/login",
        auth_uuid=args.uuid,
        timeout=8,
    )
    if status != 200:
        raise BestinError(f"로그인 확인 실패 HTTP {status}: {data}")

    safe = {}
    if isinstance(data, dict):
        for key in ("alias", "identifier", "site", "site_name", "url"):
            if key in data:
                safe[key] = data[key]
    print(json.dumps(safe or {"status": "ok"}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="IPARK/HDC BESTIN registration helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("resolve-site", help="Find HDC site code by apartment complex name")
    p.add_argument("--query", required=True, help="Apartment complex name")
    p.add_argument("--first", action="store_true", help="Use the first match if multiple matches exist")
    p.set_defaults(func=resolve_site)

    p = sub.add_parser("register", help="Send wallpad registration request")
    p.add_argument("--site-code", required=True)
    p.add_argument("--identifier", help="Building/unit, for example 101/1203")
    p.add_argument("--dong")
    p.add_argument("--ho")
    p.add_argument("--uuid", help="Use an existing UUID; generated if omitted")
    p.add_argument("--alias", default=DEFAULT_ALIAS)
    p.add_argument("--state", default=DEFAULT_STATE)
    p.set_defaults(func=register)

    p = sub.add_parser("verify", help="Verify wallpad 6-digit code")
    p.add_argument("--state", default=DEFAULT_STATE)
    p.add_argument("--code", required=True)
    p.set_defaults(func=verify)

    p = sub.add_parser("login", help="Confirm UUID login without printing tokens")
    p.add_argument("--uuid", required=True)
    p.set_defaults(func=login)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args) or 0)
    except BestinError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
