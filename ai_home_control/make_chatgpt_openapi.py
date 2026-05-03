#!/usr/bin/env python3
"""Generate a ChatGPT Actions OpenAPI schema with the public tunnel URL."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: make_chatgpt_openapi.py https://your-public-url", file=sys.stderr)
        return 2

    public_url = sys.argv[1].rstrip("/")
    if not public_url.startswith("https://"):
        print("ChatGPT Actions require a public HTTPS URL.", file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parent
    schema = json.loads((root / "openapi.json").read_text(encoding="utf-8"))
    schema["servers"] = [{"url": public_url}]

    output = root / "chatgpt_openapi.json"
    output.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
