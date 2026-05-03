---
name: ipark-bestin-register
description: Register IPARK/HDC Smart Home and BESTIN Smart Home 2.0 wallpad mobile access by collecting apartment complex, building, and unit from the user, preparing the 180-second wallpad registration flow, sending the Bestin/HDC registration request as alias "AI Assist", verifying the wallpad one-time code, and giving Home Assistant or Google Home follow-up steps. Use for Korean IPARK, 아이파크홈, 카카오홈 확장서비스, BESTIN, wallpad mobile device registration, UUID registration, or Home Assistant BESTIN version2.0 setup tasks.
---

# IPARK BESTIN Register

## Overview

Register an IPARK/HDC Smart Home BESTIN Smart Home 2.0 wallpad mobile device entry for Home Assistant by using the same server flow as the mobile app linkage: resolve complex `site`, create a UUID, ask the user to open wallpad mobile registration, send registration as `AI Assist`, then verify the 6-digit code within 180 seconds.

Use [scripts/ipark_bestin_register.py](scripts/ipark_bestin_register.py) for API calls. It uses only Python standard library.

## Safety

- Only proceed for a residence the user says they are authorized to administer.
- Do not brute-force unit numbers, OTPs, or apartment records.
- Do not expose access tokens. The reusable credential is the UUID registered to the wallpad.
- Default registration alias must be `AI Assist`, unless the user explicitly asks for another alias.
- Treat apartment name, building, unit, UUID, and tokens as sensitive.

## Connection Flow

1. Explain the flow briefly:
   - The user provides apartment complex, building, and unit.
   - AI resolves the IPARK/HDC `site` code and prepares a UUID.
   - User opens wallpad mobile device registration.
   - User types `네`.
   - AI sends registration immediately as `AI Assist`.
   - User reads the 6-digit wallpad code.
   - AI verifies the code and returns the UUID for Home Assistant BESTIN version2.0.
2. Collect apartment complex, building, and unit. Normalize building/unit as `동/호`, for example `101/1203`.
3. Resolve the site before asking the user to touch the wallpad:
   ```bash
   python3 scripts/ipark_bestin_register.py resolve-site --query "아파트단지명"
   ```
4. Prepare the exact registration command with the resolved `--site-code`, normalized `--identifier`, generated UUID, and state file path. Do not run it yet.
5. Tell the user to operate the wallpad:
   - 월패드에서 `모바일기기등록`으로 이동
   - `+ 등록` 누르기
   - “서버로부터 인증번호 수신을 기다리고 있습니다” 화면이 뜨면 채팅에 `네` 입력
6. When the user sends `네`, immediately run:
   ```bash
   python3 scripts/ipark_bestin_register.py register --site-code SITE_CODE --identifier DONG/HO --uuid UUID --alias "AI Assist" --state /tmp/ipark-bestin-register-state.json
   ```
7. Ask the user for the 6-digit code shown on the wallpad, then immediately run:
   ```bash
   python3 scripts/ipark_bestin_register.py verify --state /tmp/ipark-bestin-register-state.json --code 123456
   ```
8. Optionally confirm login:
   ```bash
   python3 scripts/ipark_bestin_register.py login --uuid UUID
   ```
9. Give the follow-up:
   - Home Assistant: install or open BESTIN custom integration, choose `version2.0`, paste UUID, set elevator count/address if needed.
   - Google Home: expose the resulting Home Assistant entities through Home Assistant Cloud / Google Assistant, then link `Home Assistant Cloud by Nabu Casa` in Google Home.
   - Ask whether the user wants help installing Home Assistant, BESTIN, HACS, or Google Home integration tools.

## Timing Notes

- Do all non-timed work before wallpad registration: site lookup, identifier normalization, UUID generation, and command preparation.
- The 180-second window starts after the user opens wallpad registration. In that window only run `register`, ask for the code, and run `verify`.
- If `registration` does not return a transaction, tell the user to restart wallpad registration and verify site code and `동/호`.
- If `verify` fails, assume timeout or wrong OTP first; do not retry many codes.

## Known Verified API Shape

The working IPARK/HDC flow uses:

- `GET https://center.hdc-smart.com/v3/auth/valley` to find complex/site metadata.
- `POST https://center.hdc-smart.com/v3/auth/registration` with header `Authorization: UUID` and JSON body `{"site":"SITE_CODE","identifier":"DONG/HO","alias":"AI Assist"}`.
- `POST https://center.hdc-smart.com/v3/auth/verify` with header `Authorization: UUID` and JSON body `{"transaction":"...","password":"123456"}`.
- `POST https://center.hdc-smart.com/v3/auth/login` with header `Authorization: UUID` to verify registration and discover the center URL.

Use the script rather than hand-writing curl unless debugging.
