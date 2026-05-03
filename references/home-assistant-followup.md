# Home Assistant and Google Home Follow-Up

After BESTIN registration succeeds:

1. Home Assistant BESTIN:
   - Ensure the custom integration `ha-bestin` is installed.
   - Go to `Settings > Devices & services > Add integration`.
   - Search `BESTIN`.
   - Select `version2.0`.
   - Paste the UUID printed by the registration script.
   - If elevator support is needed, enter elevator count and the wallpad/elevator address expected by the integration.

2. Verify entities:
   - Check BESTIN devices and entities.
   - Confirm lights, electric switches, ventilation, thermostats, and optional elevator are present.
   - Rename entities and assign Home Assistant areas before exposing to Google Home.

3. Google Home:
   - Prefer Home Assistant Cloud / Nabu Casa.
   - In Home Assistant, enable Google Assistant under voice assistant/cloud settings.
   - Expose only useful entities first, especially lights, climate, fan, and selected switches.
   - In Google Home, add `Home Assistant Cloud by Nabu Casa` under `Works with Google Home`.
   - Say “Hey Google, sync my devices” after renaming or exposing new entities.

Ask the user whether they want help installing Home Assistant, Docker Desktop, HACS, ha-bestin, or Google Home integration.
