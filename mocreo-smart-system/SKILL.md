---
name: mocreo-smart-system
description: MOCREO Smart System skill. Supports H5Pro, H6Pro, NS series devices with asset management, monitoring, history, and API key control.
version: 1.3.0
tools: [ "run_shell_command" ]
---

# MOCREO Smart System Skill

## Triggering
- When users ask about MOCREO Smart System devices (H5Pro, H6Pro, NS1/NS2/NS3, etc.).
- When users need account operations, asset management, device monitoring, history queries, or data export.

## Environment (AI Handles Automatically)

**Dependencies**: If a script fails with `ModuleNotFoundError`, auto-run from repo root:
```bash
pip install -r requirements.txt
```
Try `pip3` or `python -m pip install requests python-dotenv` if that fails. Never ask the user to install packages.

**Credentials**:
1. Check if `.env` exists at the repo root (`../../.env` relative to `scripts/`).
2. If missing: tell the user their credentials will be saved locally, ask for email and password (and optionally API key). Then create `.env` yourself using your file-writing tool. Use variables `MOCREO_V3_EMAIL`, `MOCREO_V3_PASS`, and `MOCREO_V3_API_KEY`.
3. Never guess credentials. Never ask for them again in chat once saved.
4. If login returns 401: tell the user their credentials look wrong and ask them to update `.env` directly — do not ask them to type the password in chat.

**Token lifecycle**:
1. After login, save both `access_token` and `refresh_token` from the JSON output.
2. If any API call returns 401: automatically run `scripts/v3_refresh_token.py` with the saved tokens, then retry the original call.
3. If refresh also fails: inform the user the session has expired and re-run login.

## Output Contract
- **stdout**: JSON data on success (parse this for chaining)
- **stderr**: Error messages only
- **exit code**: `0` = success, `1` = failure

## Script Location
All scripts are in `scripts/`. Always run from the skill root:
```bash
python scripts/v3_login.py [args]
```

## Timestamp Format
All `--start` and `--end` use **millisecond** Unix timestamps:
```bash
python -c "import time; print(int(time.time()*1000))"          # now
python -c "import time; print(int((time.time()-86400)*1000))"   # 24h ago
```

## Instructions

1. **Atomic Operations First**: All tasks must use the existing 15 scripts. Do not write new scripts.
2. **Standard Flow**:
   - Login → get token
   - List assets (`v3_list_assets.py`) to find Asset ID
   - List devices (`v3_list_devices.py`) under that asset to find Device ID
   - Execute specific operations using those IDs
3. **Authentication Modes**:
   - Management scripts (user, API keys, asset list) require a Bearer Token.
   - Business scripts (asset/device/history) accept either `--auth <TOKEN>` or `--auth <API_KEY> --apikey`.

## Atomic Scripts (15)

### User & Auth (2)
- `v3_login.py`: `--email` `--password` → full JSON (access_token + refresh_token)
- `v3_refresh_token.py`: `--token` `--refresh_token` → new token JSON

### API Keys (3)
- `v3_create_apikey.py`: `--token` `--asset_id` `--name` `--permissions` → new key info
- `v3_list_apikeys.py`: `--token` `--asset_id` → all API keys
- `v3_delete_apikey.py`: `--token` `--asset_id` `--prefix` → delete key by prefix

### Assets (4)
- `v3_list_assets.py`: `--token` → all assets
- `v3_get_asset_details.py`: `--auth` `--asset_id` [`--apikey`] → asset config
- `v3_update_asset.py`: `--auth` `--asset_id` `--name` [`--apikey`] → rename asset
- `v3_update_asset_config.py`: `--auth` `--asset_id` `--config` [`--apikey`] → update timezone, city, etc.

### Devices & Monitoring (6)
- `v3_list_devices.py`: `--auth` `--asset_id` [`--apikey`] → all devices
- `v3_get_device_details.py`: `--auth` `--asset_id` `--device_id` [`--apikey`] → real-time status (temp, battery, online)
- `v3_update_device_name.py`: `--auth` `--asset_id` `--device_id` `--name` [`--apikey`] → rename device
- `v3_get_device_signal.py`: `--auth` `--asset_id` `--device_id` [`--apikey`] → signal strength with gateway
- `v3_get_device_history.py`: `--auth` `--asset_id` `--device_id` `--start` `--end` `--tz` `--field` [`--apikey`] → historical data
- `v3_export_device_history.py`: `--auth` `--asset_id` `--device_id` `--email` `--start` `--end` `--tz` `--fields` [`--apikey`] → export to email

## Example Workflow

```bash
# Login — outputs full JSON with access_token and refresh_token
TOKEN=$(python scripts/v3_login.py | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
REFRESH=$(python scripts/v3_login.py | python -c "import sys,json; print(json.load(sys.stdin)['refresh_token'])")

# Find Asset ID
python scripts/v3_list_assets.py --token "$TOKEN"

# List devices under an asset
python scripts/v3_list_devices.py --auth "$TOKEN" --asset_id <ASSET_ID>

# Get device history for the past 24 hours
START=$(python -c "import time; print(int((time.time()-86400)*1000))")
END=$(python -c "import time; print(int(time.time()*1000))")
python scripts/v3_get_device_history.py --auth "$TOKEN" \
  --asset_id <ASSET_ID> --device_id <DEVICE_ID> \
  --start "$START" --end "$END" --tz "Asia/Shanghai" --field "temperature"

# Export data to email
python scripts/v3_export_device_history.py --auth "$TOKEN" \
  --asset_id <ASSET_ID> --device_id <DEVICE_ID> --email user@example.com \
  --start "$START" --end "$END" --tz "Asia/Shanghai" --fields "temperature,humidity"

# Refresh when token expires (do this automatically, don't ask the user)
TOKEN=$(python scripts/v3_refresh_token.py --token "$TOKEN" --refresh_token "$REFRESH" \
  | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('result', d)['access_token'])")
```
