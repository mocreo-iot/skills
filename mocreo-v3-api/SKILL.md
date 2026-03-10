---
name: mocreo-v3-api
description: MOCREO v3 Public API skill for MOCREO Smart System devices. Supports modular, parameter-driven scripts for auth, listing, and monitoring.
version: 1.3.0
tools: [ "run_shell_command" ]
---

# MOCREO v3 Public API Skill

## Triggering
- When users ask to query the status, details, or historical monitoring data of the MOCREO Smart System (H5Pro, H6Pro, NS1-3, etc.).
- When needing to execute account operations like account login, Token refresh, API Key management (create/query/delete).
- When needing to execute asset management (list/details/rename/config update) or device management (list/details/rename/signal/history/export).

## Setup Instructions (For AI Agents)
1. If credentials (email, password, API key) are missing from the environment or not provided by the user, **DO NOT** attempt to guess them.
2. Ask the user for their MOCREO v3 credentials and explain that they can be saved locally in a `.env` file for future use to protect their privacy.
3. Offer to create the `.env` file for the user automatically using the `write_file` tool once they provide the information. Ensure the variables used are `MOCREO_V3_EMAIL`, `MOCREO_V3_PASS`, and `MOCREO_V3_API_KEY` as appropriate.
4. **CRITICAL PRIVACY RULE**: If login fails due to incorrect credentials or other reasons, **DO NOT** ask the user to provide their login credentials or any private information directly in the chat. Instead, instruct them to update their `.env` file locally.

## Instructions - CRITICAL
1. **Atomic Operations First**: Do not create new scripts based on temporary needs. All tasks must be accomplished by combining the existing 15 atomic scripts.
2. **Composite Logic Flow**:
   - **Step 1**: Use `v3_login.py` or `v3_refresh_token.py` to get a temporary Token.
   - **Step 2**: Use the Token to get Asset ID (`v3_list_assets.py`) or Device ID (`v3_list_devices.py`).
   - **Step 3**: Based on the ID, execute specific business operations (e.g., rename, query signal, export data).
3. **Authentication Modes**:
   - Management scripts (User/API Keys/Asset List) strictly require a `Bearer Token`.
   - Business scripts (Asset/Device/History) support dual authentication: defaults to using `--auth <TOKEN>`; if using an API Key, the `--apikey` flag must be added.
4. **Stability Guarantee**: Once a script passes verification via `SKILL_TEST_REPORT.md`, modifying the core logic is strictly prohibited.

## Atomic Scripts List (15 Scripts)

### 1. User & Auth (2)
- `v3_login.py`: Takes `--email`, `--password`; outputs `access_token`.
- `v3_refresh_token.py`: Takes `--token`, `--refresh_token`; refreshes and outputs new `access_token`.

### 2. API Keys Management (3)
- `v3_create_apikey.py`: Takes `--token`, `--asset_id`, `--name`, `--permissions`; creates and returns new Key info.
- `v3_list_apikeys.py`: Takes `--token`, `--asset_id`; lists all API Keys under the asset.
- `v3_delete_apikey.py`: Takes `--token`, `--asset_id`, `--prefix`; deletes API Key by prefix.

### 3. Assets Management (4)
- `v3_list_assets.py`: Takes `--token`; lists all assets under the current account.
- `v3_get_asset_details.py`: Takes `--auth`, `--asset_id` [--apikey]; gets asset configuration details.
- `v3_update_asset.py`: Takes `--auth`, `--asset_id`, `--name` [--apikey]; updates asset display name.
- `v3_update_asset_config.py`: Takes `--auth`, `--asset_id`, `--config` [--apikey]; updates timezone, city, etc.

### 4. Devices & Monitoring (6)
- `v3_list_devices.py`: Takes `--auth`, `--asset_id` [--apikey]; lists all devices under the asset.
- `v3_get_device_details.py`: Takes `--auth`, `--asset_id`, `--device_id` [--apikey]; gets real-time status (temp, battery, online, etc.).
- `v3_update_device_name.py`: Takes `--auth`, `--asset_id`, `--device_id`, `--name` [--apikey]; modifies device display name.
- `v3_get_device_signal.py`: Takes `--auth`, `--asset_id`, `--device_id` [--apikey]; queries device proxy signal with gateway.
- `v3_get_device_history.py`: Takes `--auth`, `--asset_id`, `--device_id`, `--start`, `--end`, `--tz`, `--field` [--apikey]; queries historical data points.
- `v3_export_device_history.py`: Takes `--auth`, `--asset_id`, `--device_id`, `--email`, `--start`, `--end`, `--tz`, `--fields` [--apikey]; triggers data export to email.

## Example Workflow
1. `python v3_login.py --email user@example.com --password 'pass'` -> Get Token
2. `python v3_list_assets.py --token <TOKEN>` -> Find Asset ID
3. `python v3_get_device_history.py --auth <TOKEN> --asset_id <AID> --device_id <DID> --start 1772528647000 --end 1772615047000 --tz "Asia/Shanghai" --field "temperature"`