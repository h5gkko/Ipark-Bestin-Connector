# IPARK BESTIN Connector

Unofficial helper for registering IPARK/HDC Smart Home and BESTIN Smart Home 2.0 wallpad mobile access so Home Assistant can connect through the BESTIN custom integration.

This repository is packaged as a Codex skill plus a small Python helper script. The script resolves an apartment complex site code, prepares a UUID, sends the wallpad mobile-device registration request as `AI Assist`, verifies the 6-digit wallpad code, and prints the UUID to use in Home Assistant.

## Important Notice

This project is not affiliated with, endorsed by, or supported by HDC, IPARK, BESTIN, Kakao, Google, Home Assistant, or Nabu Casa.

The flow uses undocumented IPARK/HDC Smart Home endpoints observed from public client behavior and verified by normal wallpad registration. Those endpoints may change or stop working. Use only for a residence you own or are authorized to administer.

Do not commit real UUIDs, access tokens, apartment unit numbers, one-time codes, or Home Assistant storage files.

## What This Does

- Finds the HDC/IPARK site code for an apartment complex name.
- Normalizes building/unit input as `dong/ho`, for example `101/1203`.
- Generates or accepts a UUID for BESTIN Smart Home 2.0 mobile registration.
- Sends registration with alias `AI Assist`.
- Verifies the 6-digit code displayed on the wallpad within the 180-second window.
- Prints the UUID for Home Assistant BESTIN `version2.0`.

## What This Does Not Do

- It does not bypass wallpad authorization.
- It does not brute-force apartment units or verification codes.
- It does not store or print HDC access tokens.
- It does not directly control home devices. Device control is handled by Home Assistant after the BESTIN integration is configured.

## Install As A Codex Skill

Clone this repository into your Codex skills directory:

```bash
git clone https://github.com/h5gkko/Ipark-Bestin-Connector.git ~/.codex/skills/ipark-bestin-register
```

Then ask Codex something like:

```text
아이파크/BESTIN 월패드를 AI Assist 이름으로 Home Assistant에 연결해줘.
```

## Manual Usage

All commands use Python standard library only.

Find the site code:

```bash
python3 scripts/ipark_bestin_register.py resolve-site --query "아파트단지명" --first
```

Prepare a UUID:

```bash
UUID=$(uuidgen | tr '[:upper:]' '[:lower:]')
echo "$UUID"
```

Open the wallpad mobile registration screen first:

1. Go to `모바일기기등록` on the wallpad.
2. Press `+ 등록`.
3. Wait for the screen that says it is waiting for a server verification number.

Then send the registration request immediately:

```bash
python3 scripts/ipark_bestin_register.py register \
  --site-code SITE_CODE \
  --identifier 101/1203 \
  --uuid "$UUID" \
  --alias "AI Assist" \
  --state /tmp/ipark-bestin-register-state.json
```

When the wallpad shows the 6-digit code, verify it:

```bash
python3 scripts/ipark_bestin_register.py verify \
  --state /tmp/ipark-bestin-register-state.json \
  --code 123456
```

Optionally confirm login without printing tokens:

```bash
python3 scripts/ipark_bestin_register.py login --uuid "$UUID"
```

## Home Assistant

After registration succeeds:

1. Install the BESTIN custom integration for Home Assistant.
2. Add integration `BESTIN`.
3. Choose `version2.0`.
4. Paste the UUID printed by the script.
5. Verify discovered lights, switches, ventilation, thermostat, and optional elevator entities.
6. Rename entities and assign Home Assistant areas before exposing them to Google Home.

## Google Home

The practical route is through Home Assistant:

1. Configure BESTIN entities in Home Assistant.
2. Use Home Assistant Cloud / Nabu Casa or the manual Google Assistant integration.
3. Expose only useful entities first, such as lights, climate, fan, and selected switches.
4. Link `Home Assistant Cloud by Nabu Casa` in the Google Home app.
5. Say `Hey Google, sync my devices` after changes.

## Publishing And Safety Checklist

Before making examples or logs public, check that they do not include:

- Real apartment building/unit.
- Real UUID.
- Access tokens or Home Assistant `.storage` files.
- One-time verification codes.
- Screenshots showing private residence details.

## License

No license has been selected yet. Add a `LICENSE` file before encouraging broad reuse or accepting contributions.
