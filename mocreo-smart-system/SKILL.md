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
3. Store shared login credentials in the repo-root `.env` using `MOCREO_USER`, `MOCREO_PASS`, and `MOCREO_PLATFORM`. Store Smart System API keys in the local asset-scoped registry `.mocreo_v3_apikeys.json`, grouped by `asset_id` and permission profile. Create that registry file automatically the first time a Smart System API key is saved.
4. Password entry must happen in the terminal with hidden input. Never ask the user to type a password in chat or manually edit `.env` unless they explicitly want to.
5. Treat `MOCREO_PLATFORM=smart` as the default routing hint for Smart System requests.
6. If login fails after credentials were found, treat it as a configured-but-invalid state rather than a missing-setup state. Tell the user the saved account, password, or selected platform may be wrong, and ask them to rerun the bootstrap with the correct platform or update `.env` directly.

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

1. **Atomic Operations First**: All tasks must use the existing Smart System scripts. Prefer the resolver and atomic scripts that already exist in this folder before considering any new helper code.
2. **Standard Flow**:
   - Login -> get token
   - List assets (`v3_list_assets.py`) to find Asset ID
   - For asset-scoped scripts that support both auth modes, first resolve the best saved API key for the selected asset from the local registry with `v3_resolve_apikey.py`, then prefer that API key by default
   - List devices (`v3_list_devices.py`) under that asset to find Device ID
   - Execute specific operations using those IDs
3. **Authentication Modes**:
   - Management scripts (user login, refresh, asset list, API key create/list/delete) require a Bearer Token.
   - Public asset/device business APIs are documented as `X-API-Key` APIs. In this skill, those scripts accept either `--auth <TOKEN>` or `--auth <API_KEY> --apikey`.
   - Default policy: whenever a script supports both auth modes, use API Key by default rather than Bearer Token.
   - Do not skip the API key resolution step for supported asset-scoped routes. Token is not the default shortcut for those routes.
   - Keep using Bearer Token only for flows that require it, such as login, token refresh, asset listing, and API key management.
   - Do not silently create a new API key just to satisfy that preference. If no suitable saved API key is available in the local registry for the selected asset, fall back to Bearer Token unless the user explicitly asks to create or save an API key.
   - Remember that API keys are asset-bound. Resolve them by `asset_id`, and prefer a key whose saved permission profile matches the requested operation.
   - For supported asset-scoped routes, the expected order is: resolve local registry key -> try API Key -> only then fall back to Bearer Token if no suitable key exists or the API-key path fails in an allowed fallback case.
   - If an API-key-backed request returns `403` with a permission message such as `Forbidden: API Key does not have the required permissions`, tell the user the API key is valid but lacks the required permission for that operation. Do not describe that case as bad credentials, missing setup, or an expired session.
   - If a token-backed management request such as API key creation, listing, or deletion returns `403`, tell the user their signed-in account lacks sufficient role permissions on that asset for that management action. Do not describe that case as a bad login, expired token, or missing API key.
   - Use these response patterns for permission-denied cases:
     - API key permission failure: `The API key is valid, but it does not have enough permission for this action. This operation requires a write-capable permission on the selected asset or device, and the current key does not include it.`
     - Account role permission failure: `Your account does not have sufficient permission on this asset to perform this management action. This is an asset-role restriction, not a login or token issue. Please contact the asset creator or administrator to elevate your asset-management permission.`
   - If an API-key-backed request returns an unexpected server-side failure such as `500 Internal Server Error`, retry that same asset-scoped request once with Bearer Token before concluding the operation failed. Explain that the API-key path for that route appears unsupported or unstable for the current server behavior.
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
   - For asset-scoped reads and writes, assume API Key is the default credential when a valid saved key for that asset is available in the local registry.
   - Only create an API key when the user explicitly asks for one or when a temporary test requires it.
   - Use the narrowest permissions possible. Prefer `device.read` unless the user clearly needs write access.
   - Relevant documented permissions include `asset.read`, `asset.update`, `device.read`, and `device.update`.
   - The full API key is only returned once. If you create one for immediate use, capture it from the create response and use it right away.
   - These scripts run in a non-interactive shell. Never rely on their built-in terminal prompts — resolve all decisions in chat first, then pass the appropriate flags.
   - **Creating a key**: Save the returned key into the local asset-scoped registry with the selected `asset_id`, permission list, and derived tier.
   - **Deleting a key**: Confirm with the user in chat before running. Always pass `--force` so the script does not prompt.
   - The local registry can keep multiple asset-specific keys at the same time. Do not collapse them back into a single global API key field.
   - When creating a new key, save it into the local asset-scoped registry with its `asset_id`, permission list, and derived tier such as `read` or `write`.
   - Temporary test keys must be deleted in the same session with `v3_delete_apikey.py`.
   - API keys are asset-bound and cannot be reused across assets.
   - Respect documented rate limits for API-key traffic: at most 1000 requests per hour and at most 3 concurrent requests per key.
   - Read-only permissions such as `device.read` are not sufficient for write operations such as renaming a device. Those operations require a write-capable permission such as `device.update`.
   - API key management itself is a privileged asset-management action. Even with a valid account token, the signed-in user may still be forbidden from creating, listing, or deleting API keys on an asset they do not administratively control.
   - Use these standard success-message patterns for API key lifecycle events:
     - First key saved for an asset: `Created a new API key for [Asset Name] and saved it in the local asset-scoped key registry. This is the first saved key for that asset in your local registry.`
     - Additional key saved for the same asset: `Created a new API key for [Asset Name] and saved it in the local asset-scoped key registry. This asset already had saved keys, and the new key was added alongside them instead of replacing them.`
     - First read-tier key saved for an asset: `Created and saved a read-capable API key for [Asset Name]. This key can be used for asset-scoped read operations supported by its permission set.`
     - First write-tier key saved for an asset: `Created and saved a write-capable API key for [Asset Name]. This key can be used for asset-scoped update operations supported by its permission set.`
     - Additional read-tier key saved for an asset: `Created and saved another read-capable API key for [Asset Name]. Your local registry now keeps more than one saved key for this asset.`
     - Additional write-tier key saved for an asset: `Created and saved another write-capable API key for [Asset Name]. Your local registry now keeps more than one saved key for this asset.`
     - First key saved for a different asset: `Created a new API key for [Asset Name] and saved it in the local asset-scoped key registry. This does not replace keys saved for other assets.`
     - Registry auto-created: `The local Smart System API key registry did not exist yet, so it was created automatically when this key was saved.`
     - Key deleted successfully: `Deleted the API key successfully and removed its saved record from the local asset-scoped key registry.`
   - When reporting API key creation success, tell the user whether the key was saved as a read-tier or write-tier key, whether it was the first saved key for that asset, and whether the local registry file had to be created automatically.
   - When reporting API key deletion success, tell the user that the key was removed both from the server-side asset and from the local asset-scoped registry when that local record existed.
7. **Signal and Export Interpretation**:
   - `v3_get_device_signal.py` may return `success=true` with `result=null`; do not treat that alone as a script failure.
   - If signal data is needed, prefer LoRa or hub-connected devices such as `LS1` over Wi-Fi-only devices.
   - `v3_export_device_history.py` triggers a real export action. Use it only when the user explicitly asks to export or email data.
   - The public API documents export as sending a download link to the specified email. When export succeeds, report the returned download URL and mention the destination email used.
   - The export API is time-range-based, not record-count-based. Do not describe it as exporting an exact number of rows unless the API has already proven that behavior for the same request shape.
   - If the user asks for "latest N records" and also wants an export email, first use `v3_get_device_history.py` with `--limit N` to identify the target records, then export the time range covering them. Explain that the exported file may contain a slightly different row count because export uses `from`/`to` boundaries rather than `limit`.
   - When converting "latest N records" into an export window, add a small safety buffer before the oldest selected timestamp and after the newest selected timestamp instead of using exact boundaries, to reduce the chance of dropping a row at either export boundary.
8. **Default Selection Strategy**:
   - If the user does not specify an asset, list assets first and select the most relevant owned asset based on the request.
   - If the user does not specify a device, list devices under the chosen asset and match by display name, model, or device type.
   - Do not guess a destructive target. If multiple assets or devices are plausible for a mutating request, ask a short clarifying question.
9. **User-Facing Formatting Rules**:
   - Before presenting temperature readings, timestamps, or export expectations to the user, fetch the asset details with `v3_get_asset_details.py` and use the asset config as the display source of truth when available.
   - Use `config.tz` as the default timezone for user-facing timestamps unless the user explicitly asked for a different timezone.
   - If `config.timeFormat` is `hour12`, present times in a familiar 12-hour local format such as `02/26/2026 08:58:20 AM`. If it is `hour24`, present times in a familiar 24-hour local format such as `2026-02-26 08:58:20`.
   - For temperature data, prefer the asset's configured temperature unit from `config.units.temperature` when it clearly maps to Celsius or Fahrenheit.
   - Treat clear values such as `C`, `F`, `°C`, `°F`, `℃`, or `℉` as trustworthy unit settings.
   - If terminal output garbles the unit glyph, inspect the underlying Unicode value before treating it as invalid. In particular, `\u2103` means `℃` and `\u2109` means `℉`, even if the terminal renders a different character.
   - Only treat the configured temperature unit as unreadable when the underlying value still does not map cleanly to Celsius or Fahrenheit after that normalization step. If that happens, tell the user the asset's temperature-unit setting could not be read cleanly from the server response, then fall back to the most reliable observed source for that response path.
   - If you convert temperature values for display, say which unit you are showing.
10. **History Query Rules**:
   - For `v3_get_device_history.py`, always provide `from`, `to`, `tz`, and `field`.
   - Valid `field` values are `temperature`, `humidity`, `water_leak`, `water_level`, and `frozen`.
   - Optional `windowDuration` values use compact duration strings such as `1m`, `30m`, `1h`, `1d`, or `1mo`.
   - Optional `aggregationsType` values are comma-separated combinations of `mean`, `max`, and `min`, and only make sense when `windowDuration` is provided.
   - `limit` is only for constrained result sets and should stay within `1-10000`.
   - Do not combine `limit` with aggregation parameters unless the API behavior is clearly documented for that combination.
   - Do not assume `limit=1` means "the latest reading". Treat the history endpoint as potentially returning data in ascending time order unless the API has explicitly proven otherwise.
   - When the user asks for the latest `N` readings, estimate a narrow recent time window first instead of querying a very large range. Use a default reporting-cadence assumption of one reading every 10 minutes unless the device behavior has already shown a different cadence.
   - For latest-reading requests, start with a heuristic window such as `max(6 hours, N * 10 minutes * 12)` and request enough rows to cover that window comfortably.
   - After the data is returned, sort the records by `time` in ascending order yourself and take the final `N` rows as the latest readings.
   - If the initial window does not return enough rows, automatically widen the time range and retry before telling the user the data is missing.
11. **Export Query Rules**:
   - For `v3_export_device_history.py`, always provide `email`, `from`, `to`, `tz`, and `fields`.
   - Valid `fields` values are comma-separated combinations of `temperature`, `humidity`, `water_leak`, `water_level`, and `frozen`.
   - Optional export aggregation uses the same `windowDuration` and `aggregationsType` rules as history queries.
   - Use the user's explicitly requested email when provided; otherwise use the confirmed default email for the current account.
   - Do not present `v3_export_device_history.py` as supporting `limit`; it does not.
   - For requests framed as "export the latest N records", tell the user you are exporting the time range that covers those records, not guaranteeing an exact row count in the exported file.
   - Although the script accepts `--apikey`, if the export call fails with an unexpected server error when using API Key, retry with Bearer Token and treat Bearer Token as the practical fallback for export on that asset.

## Scripts

### User & Auth (2)
- `v3_login.py`: `--email` `--password` -> full JSON (access_token + refresh_token)
- `v3_refresh_token.py`: `--token` `--refresh_token` -> new token JSON

### API Keys (4)
- `v3_create_apikey.py`: `--token` `--asset_id` `--name` `--permissions` [`--expires_at`] [`--asset_name`] -> new key info
- `v3_list_apikeys.py`: `--token` `--asset_id` -> all API keys
- `v3_delete_apikey.py`: `--token` `--asset_id` `--prefix` [`--force`] -> delete key by prefix
- `v3_resolve_apikey.py`: `--asset_id` [`--permissions`] [`--tier`] -> best saved API key record for that asset from the local registry

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
