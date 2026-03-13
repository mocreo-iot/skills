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
1. Do not proactively read `.env`. Run `scripts/v3_login.py` as the first step. If it exits with code `2` and stderr contains `MOCREO_CREDENTIALS_MISSING`, output the fixed "Credential Missing" response defined in the root `SKILL.md` verbatim and wait for the user to confirm setup is complete before continuing.
2. The bootstrap identifies the platform by guided questions about the app, hub model, or sensor family. It uses this mapping:
   - `MOCREO Smart App` = `MOCREO Smart System` = `MOCREO V3`
   - V3 hubs: `H3`, `H5-Lite`, `H5-Pro`, `H6-Lite`, `H6-Pro`
   - V3-only sensors: `MS2`, `LS1`, `LS2`, `LS3`, `LW1`, `LD1`, `LB1`, `NS1`, `NS2`, `NS3`
   - Shared sensors needing a follow-up question: `ST5`, `ST6`, `ST8`, `ST9`, `ST10`, `MS1`, `SW2`
3. Store credentials in the repo-root `.env` using `MOCREO_USER`, `MOCREO_PASS`, `MOCREO_PLATFORM`, and optionally `MOCREO_V3_API_KEY`.
4. Password entry must happen in the terminal with hidden input. Never ask the user to type a password in chat or manually edit `.env` unless they explicitly want to.
5. Treat `MOCREO_PLATFORM=smart` as the default routing hint for Smart System requests.
6. If login returns 401: tell the user their credentials look wrong and ask them to re-run the bootstrap or update `.env` directly.

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
   - Login -> get token
   - List assets (`v3_list_assets.py`) to find Asset ID
   - List devices (`v3_list_devices.py`) under that asset to find Device ID
   - Execute specific operations using those IDs
3. **Authentication Modes**:
   - Management scripts (user login, refresh, asset list, API key create/list/delete) require a Bearer Token.
   - Public asset/device business APIs are documented as `X-API-Key` APIs. In this skill, those scripts accept either `--auth <TOKEN>` or `--auth <API_KEY> --apikey`.
   - Prefer Bearer Token for account-scoped management flows. Prefer API Key for asset-scoped automation flows.
4. **Mutating Operations Policy**:
   - Treat `v3_create_apikey.py`, `v3_delete_apikey.py`, `v3_update_asset.py`, `v3_update_asset_config.py`, `v3_update_device_name.py`, and `v3_export_device_history.py` as side-effecting operations.
   - Before changing anything, first read the current state with `v3_get_asset_details.py`, `v3_list_devices.py`, or `v3_get_device_details.py`.
   - After every successful change, read the resource again or report the returned value so the user can see the final state.
   - For testing or temporary operations, restore the original value in the same session whenever practical.
5. **Asset Config Guardrails**:
   - Only send fields the user explicitly asked to change.
   - Prefer small partial payloads instead of resubmitting the whole config object.
   - The public OpenAPI currently documents `city` as the canonical example field for `v3_update_asset_config.py`.
   - Safe default fields are `city`, and only other minimal fields already proven to work in practice such as `tz`, `country`, and `state`.
   - Do not send `timeFormat` by default. The API may reject it.
   - Do not resend the full `config` block unless absolutely necessary.
   - Prefer `v3_update_asset_config.py --safe` unless the user clearly needs a broader payload.
6. **API Key Safety Rules**:
   - Only create an API key when the user explicitly asks for one or when a temporary test requires it.
   - Use the narrowest permissions possible. Prefer `device.read` unless the user clearly needs write access.
   - Relevant documented permissions include `asset.read`, `asset.update`, `device.read`, and `device.update`.
   - The full API key is only returned once. If you create one for immediate use, capture it from the create response and use it right away.
   - These scripts run in a non-interactive shell. Never rely on their built-in terminal prompts — resolve all decisions in chat first, then pass the appropriate flags.
   - **Creating a key**: Ask the user in chat whether to save it as the default `MOCREO_V3_API_KEY` in `.env`. If yes, pass `--save_to_env`; if no, omit it. Always decide before running the script.
   - **Deleting a key**: Confirm with the user in chat before running. Always pass `--force` so the script does not prompt. If the deleted key was the current default, ask the user in chat whether to clear `MOCREO_V3_API_KEY` from `.env` and handle it separately if needed.
   - Do not overwrite `MOCREO_V3_API_KEY` silently. Only persist it after clear user confirmation, because API keys are asset-bound.
   - When creating a new key or when the user has multiple keys, always remind them that `.env` holds only one `MOCREO_V3_API_KEY` at a time. Scripts that accept `--apikey` will use whichever key is currently saved there. If the user switches the default, the old default is no longer used by those scripts.
   - Temporary test keys must be deleted in the same session with `v3_delete_apikey.py`.
   - API keys are asset-bound and cannot be reused across assets.
   - Respect documented rate limits for API-key traffic: at most 1000 requests per hour and at most 3 concurrent requests per key.
7. **Signal and Export Interpretation**:
   - `v3_get_device_signal.py` may return `success=true` with `result=null`; do not treat that alone as a script failure.
   - If signal data is needed, prefer LoRa or hub-connected devices such as `LS1` over Wi-Fi-only devices.
   - `v3_export_device_history.py` triggers a real export action. Use it only when the user explicitly asks to export or email data.
   - The public API documents export as sending a download link to the specified email. When export succeeds, report the returned download URL and mention the destination email used.
8. **Default Selection Strategy**:
   - If the user does not specify an asset, list assets first and select the most relevant owned asset based on the request.
   - If the user does not specify a device, list devices under the chosen asset and match by display name, model, or device type.
   - Do not guess a destructive target. If multiple assets or devices are plausible for a mutating request, ask a short clarifying question.
9. **History Query Rules**:
   - For `v3_get_device_history.py`, always provide `from`, `to`, `tz`, and `field`.
   - Valid `field` values are `temperature`, `humidity`, `water_leak`, `water_level`, and `frozen`.
   - Optional `windowDuration` values use compact duration strings such as `1m`, `30m`, `1h`, `1d`, or `1mo`.
   - Optional `aggregationsType` values are comma-separated combinations of `mean`, `max`, and `min`, and only make sense when `windowDuration` is provided.
   - `limit` is only for constrained result sets and should stay within `1-10000`.
   - Do not combine `limit` with aggregation parameters unless the API behavior is clearly documented for that combination.
10. **Export Query Rules**:
   - For `v3_export_device_history.py`, always provide `email`, `from`, `to`, `tz`, and `fields`.
   - Valid `fields` values are comma-separated combinations of `temperature`, `humidity`, `water_leak`, `water_level`, and `frozen`.
   - Optional export aggregation uses the same `windowDuration` and `aggregationsType` rules as history queries.
   - Use the user's explicitly requested email when provided; otherwise use the confirmed default email for the current account.

## Atomic Scripts (15)

### User & Auth (2)
- `v3_login.py`: `--email` `--password` -> full JSON (access_token + refresh_token)
- `v3_refresh_token.py`: `--token` `--refresh_token` -> new token JSON

### API Keys (3)
- `v3_create_apikey.py`: `--token` `--asset_id` `--name` `--permissions` [`--expires_at`] [`--save_to_env`] -> new key info
- `v3_list_apikeys.py`: `--token` `--asset_id` -> all API keys
- `v3_delete_apikey.py`: `--token` `--asset_id` `--prefix` [`--force`] -> delete key by prefix

### Assets (4)
- `v3_list_assets.py`: `--token` -> all assets
- `v3_get_asset_details.py`: `--auth` `--asset_id` [`--apikey`] -> asset config
- `v3_update_asset.py`: `--auth` `--asset_id` `--name` [`--apikey`] -> rename asset
- `v3_update_asset_config.py`: `--auth` `--asset_id` `--config` [`--apikey`] [`--safe`] -> update timezone, city, etc.

### Devices & Monitoring (6)
- `v3_list_devices.py`: `--auth` `--asset_id` [`--apikey`] -> all devices
- `v3_get_device_details.py`: `--auth` `--asset_id` `--device_id` [`--apikey`] -> real-time status (temp, battery, online)
- `v3_update_device_name.py`: `--auth` `--asset_id` `--device_id` `--name` [`--apikey`] -> rename device
- `v3_get_device_signal.py`: `--auth` `--asset_id` `--device_id` [`--apikey`] -> signal strength with gateway
- `v3_get_device_history.py`: `--auth` `--asset_id` `--device_id` `--start` `--end` `--tz` `--field` [`--window`] [`--agg`] [`--limit`] [`--apikey`] -> historical data
- `v3_export_device_history.py`: `--auth` `--asset_id` `--device_id` `--email` `--start` `--end` `--tz` `--fields` [`--window`] [`--agg`] [`--apikey`] -> export to email

## Example Workflow

```bash
# Login - outputs full JSON with access_token and refresh_token
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
