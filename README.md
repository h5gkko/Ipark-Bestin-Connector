# IPARK BESTIN Connector

Unofficial helpers for connecting IPARK/HDC Smart Home and BESTIN Smart Home 2.0 wallpads to automation tools.

You can use this repository in three separate levels:

1. **IPARK/BESTIN registration only**  
   Register a wallpad mobile-device UUID as `AI Assist`, then use that UUID wherever you need BESTIN Smart Home 2.0 access.

2. **Home Assistant integration**  
   Use the registered UUID with the Home Assistant BESTIN custom integration, then organize lights, heating, ventilation, electric switches, gas valve, and optional elevator entities.

3. **Custom GPTs / AI control**  
   Put a small allowlisted bridge in front of Home Assistant so GPTs or local AI agents can control selected devices safely.

## Important Notice

This project is not affiliated with, endorsed by, or supported by HDC, IPARK, BESTIN, Kakao, Google, Home Assistant, OpenAI, Cloudflare, or Nabu Casa.

The registration flow uses undocumented IPARK/HDC Smart Home endpoints observed from normal client behavior and verified by wallpad registration. Those endpoints may change or stop working. Use only for a residence you own or are authorized to administer.

Do not commit or publish real UUIDs, access tokens, apartment unit numbers, one-time codes, Home Assistant `.storage` files, GPT Action keys, or Cloudflare tunnel URLs.

## Path 1. IPARK/BESTIN Registration Only

Use this when your only goal is to register a UUID with the wallpad.

Start here:

[docs/ipark-bestin-registration.md](docs/ipark-bestin-registration.md)

Quick version:

```bash
python3 scripts/ipark_bestin_register.py resolve-site --query "아파트단지명" --first
UUID="$(uuidgen | tr '[:upper:]' '[:lower:]')"

python3 scripts/ipark_bestin_register.py register \
  --site-code SITE_CODE \
  --identifier 101/1203 \
  --uuid "$UUID" \
  --alias "AI Assist" \
  --state /tmp/ipark-bestin-register-state.json

python3 scripts/ipark_bestin_register.py verify \
  --state /tmp/ipark-bestin-register-state.json \
  --code 123456
```

The wallpad registration window is short, so resolve the site code and prepare the command before pressing `+ 등록` on the wallpad.

## Path 2. Add Home Assistant

Use this after UUID registration succeeds.

Start here:

[docs/home-assistant.md](docs/home-assistant.md)

Home Assistant flow:

1. Install Home Assistant.
2. Install the BESTIN custom integration separately.
3. Add integration `BESTIN`.
4. Choose `version2.0`.
5. Paste the registered UUID.
6. Verify entities and assign areas.
7. Expose selected entities to Google Home only after names and areas are cleaned up.

## Path 3. Add GPTs / AI Control

Use this after Home Assistant can already control BESTIN entities.

Start here:

[docs/gpts-ai-control.md](docs/gpts-ai-control.md)

The AI bridge intentionally exposes only an allowlist:

- Lights
- Heating
- Electric switches
- Ventilation
- Elevator status and optional down call
- Gas valve close only

Safety defaults:

- Lighting uses a separate non-consequential GPT Action endpoint.
- Other control actions are consequential and should ask for confirmation.
- Gas can only be closed, never opened.
- Arbitrary Home Assistant services are not exposed.

## Codex Skill

You can install the registration workflow as a Codex skill:

```bash
git clone https://github.com/h5gkko/Ipark-Bestin-Connector.git ~/.codex/skills/ipark-bestin-register
```

Then ask Codex something like:

```text
아이파크/BESTIN 월패드를 AI Assist 이름으로 Home Assistant에 연결해줘.
```

## Repository Layout

```text
scripts/ipark_bestin_register.py      IPARK/HDC registration helper
SKILL.md                             Codex skill instructions
references/home-assistant-followup.md Short Home Assistant follow-up notes
docs/ipark-bestin-registration.md     Registration-only guide
docs/home-assistant.md                Home Assistant guide
docs/gpts-ai-control.md               Custom GPTs and AI bridge guide
ai_home_control/                      Allowlisted Home Assistant AI bridge
PRIVACY.md                            Privacy policy for Custom GPTs
SECURITY.md                           Security notes
```

## Privacy Policy URL For Custom GPTs

If this repository is public, you can use this as the GPT privacy policy URL:

```text
https://github.com/h5gkko/Ipark-Bestin-Connector/blob/main/PRIVACY.md
```

## Publishing And Safety Checklist

Before making examples, issues, screenshots, or logs public, check that they do not include:

- Real apartment complex/building/unit details.
- Real registered UUID.
- HDC/IPARK/BESTIN access tokens.
- Home Assistant long-lived access tokens.
- GPT Action bearer keys.
- Cloudflare tunnel URLs used by your live bridge.
- Home Assistant `.storage` files.
- One-time verification codes.
- Screenshots showing private residence details.

## License

No license has been selected yet. Add a `LICENSE` file before encouraging broad reuse or accepting contributions.
