# IPARK/BESTIN Registration Only

This path registers a UUID to an IPARK/HDC Smart Home and BESTIN Smart Home 2.0 wallpad. It does not require Home Assistant.

## What You Need

- Authorization to administer the residence.
- Apartment complex name.
- Building and unit in `동/호` format, for example `101/1203`.
- Access to the wallpad `모바일기기등록` screen.
- Python 3.

The helper script uses only the Python standard library.

## What The Script Does

1. Resolves an apartment complex name to an IPARK/HDC `site` code.
2. Generates or accepts a UUID.
3. Sends a mobile-device registration request using alias `AI Assist`.
4. Verifies the 6-digit code displayed by the wallpad.
5. Optionally confirms login with the registered UUID.

It does not bypass wallpad authorization and does not brute-force codes.

## Step 1. Resolve Site Code

```bash
python3 scripts/ipark_bestin_register.py resolve-site --query "아파트단지명"
```

If the correct complex is obvious:

```bash
python3 scripts/ipark_bestin_register.py resolve-site --query "아파트단지명" --first
```

Keep the returned site code ready.

## Step 2. Prepare UUID

```bash
UUID="$(uuidgen | tr '[:upper:]' '[:lower:]')"
echo "$UUID"
```

Do not publish this UUID after it is registered.

## Step 3. Prepare The Command Before Touching The Wallpad

Replace `SITE_CODE` and `101/1203` first:

```bash
python3 scripts/ipark_bestin_register.py register \
  --site-code SITE_CODE \
  --identifier 101/1203 \
  --uuid "$UUID" \
  --alias "AI Assist" \
  --state /tmp/ipark-bestin-register-state.json
```

Do not run it yet.

## Step 4. Open Wallpad Registration

On the wallpad:

1. Open `모바일기기등록`.
2. Press `+ 등록`.
3. Wait until it says it is waiting for a server verification number.

Now run the prepared `register` command immediately.

## Step 5. Verify The Wallpad Code

When the wallpad shows the 6-digit code:

```bash
python3 scripts/ipark_bestin_register.py verify \
  --state /tmp/ipark-bestin-register-state.json \
  --code 123456
```

The wallpad registration window is usually short. If it times out, restart the wallpad registration and repeat the `register` and `verify` steps.

## Step 6. Optional Login Check

```bash
python3 scripts/ipark_bestin_register.py login --uuid "$UUID"
```

This checks that the UUID is usable without printing access tokens.

## Verified API Shape

The script wraps this observed flow:

- `GET https://center.hdc-smart.com/v3/auth/valley`
- `POST https://center.hdc-smart.com/v3/auth/registration`
- `POST https://center.hdc-smart.com/v3/auth/verify`
- `POST https://center.hdc-smart.com/v3/auth/login`

Use the script rather than hand-writing requests unless debugging.
