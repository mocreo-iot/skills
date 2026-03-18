---
name: mocreo-sensor-system
description: MOCREO Sensor System skill for battery, status, alerts, node data, and monitoring queries on V2 hubs and sensor nodes.
version: 1.0.1
tools: [ "run_shell_command" ]
---

# MOCREO Sensor System Skill

Before using this sub-skill directly, check the root router skill at `skills/mocreo-api/SKILL.md` and follow its routing rules first.

## Triggering
- When users ask to query MOCREO Sensor System data.
- When users ask to manage devices (hubs), nodes (sensors), or alerts.

## Environment (AI Handles Automatically)

**Dependencies**: If a script fails with `ModuleNotFoundError`, do not install packages silently.
```bash
pip install -r requirements.txt
```
Before any install attempt, tell the user which command you want to run and ask for permission because it may modify the current Python environment or a global environment when no virtual environment is active.
If a virtual environment is already active, prefer installing there after the user agrees.
If no virtual environment is active, explicitly warn that the install may go to the current or global Python environment and ask again before proceeding.
If the user does not approve, stop and provide the exact manual install command instead.
Try `pip3` or `python -m pip install requests python-dotenv` only after the user has agreed to dependency installation.

**Credentials**:
1. Do not proactively read `.env`. Run `python skills/mocreo-sensor-system/scripts/v2_login.py` from the repository root as the first step. If it exits with code `2` and stderr contains `MOCREO_CREDENTIALS_MISSING`, output the fixed "Credential Missing" response defined in the root `SKILL.md` verbatim and wait for the user to confirm setup is complete before continuing.
2. The bootstrap identifies the platform by guided questions about the app, hub model, or sensor family. It uses this mapping:
   - `MOCREO Sensor App` = `MOCREO Sensor System` = `MOCREO V2`
   - V2 hubs: `H1`, `H2`
   - V2-only sensors: `ST1`, `ST2`, `ST3`, `ST4`, `ST7`, `ST7-CL`, `SS1`, `NM1`
   - Shared sensors needing a follow-up question: `ST5`, `ST6`, `ST8`, `ST9`, `ST10`, `MS1`, `SW2`
3. Store credentials in the repo-root `.env` using `MOCREO_USER`, `MOCREO_PASS`, and `MOCREO_PLATFORM`.
4. Password entry must happen in the terminal with hidden input. Never ask the user to type a password in chat or manually edit `.env` unless they explicitly want to.
5. Treat `MOCREO_PLATFORM=sensor` as the routing hint only after the root router has selected this sub-skill. Do not treat the word `sensor` by itself as proof that the account belongs to Sensor System.
6. If login fails after credentials were found, treat it as a configured-but-invalid state rather than a missing-setup state. Tell the user the saved account, password, or selected platform may be wrong, and ask them to rerun the bootstrap with the correct platform or update `.env` directly.

**Token lifecycle**:
1. After login, save both `access_token` and `refresh_token` from the JSON output.
2. If any API call returns 401: automatically run `python skills/mocreo-sensor-system/scripts/v2_refresh_token.py` from the repository root with the saved refresh token, then retry the original call.
3. If refresh also fails: inform the user the session has expired and re-run login.

## Output Contract
- **stdout**: JSON data on success (parse this for chaining)
- **stderr**: Error messages only
- **exit code**: `0` = success, `1` = failure

## Script Location
All Sensor System scripts are in `skills/mocreo-sensor-system/scripts/`. Always run from the repository root:
```bash
python skills/mocreo-sensor-system/scripts/v2_login.py [args]
```

## Instructions
1. **Architecture**: Uses username/password to get an OAuth token, then passes that token as a Bearer header on all subsequent calls.
2. **Standard Flow**:
   - Login -> get token
   - List devices (`v2_list_devices.py`) or nodes (`v2_list_nodes.py`) to find IDs
   - Use IDs for specific operations (samples, alerts, etc.)
3. **Live Swagger alignment**:
   - The online Sensor System Swagger currently documents token fields at the top level: `accessToken`, `refreshToken`, `accessTokenExpiresAt`, `refreshTokenExpiresAt`.
   - The live API responses observed during testing are wrapped as `{ code, data, requestId }`, so `v2_login.py` and `v2_refresh_token.py` outputs should be parsed from `data.accessToken` and `data.refreshToken`.
   - Sample and alert time filters use `beginTime` / `endTime` in seconds.
   - Alerts support `limit`, `offset`, `dismissed`, `beginTime`, and `endTime`. The live Swagger does not document a `nodeId` filter on `/alerts`, so do not rely on node-scoped alert filtering.
   - The `samples` endpoint is model-limited in live behavior. Do not assume every V2 node supports history retrieval.
   - Treat `ST1`, `ST2`, `ST3`, `ST4`, `ST7`, and `ST8` as unsupported for `v2_get_node_samples.py` unless the live API later proves otherwise for a specific account or firmware.
   - `ST6` and `ST9` have been verified to return sample history successfully in live testing.

## Available Scripts (11)

### Auth & User
- `v2_login.py`: `--username` `--password` -> full OAuth envelope (`data.accessToken` + `data.refreshToken`)
- `v2_refresh_token.py`: `--refresh_token` -> new token envelope (`data.accessToken` + `data.refreshToken`)
- `v2_get_user.py`: `--token` -> current user info

### Devices (Hubs)
- `v2_list_devices.py`: `--token` -> list all hubs
- `v2_get_device.py`: `--token` `--sn` -> specific hub details

### Nodes (Sensors)
- `v2_list_nodes.py`: `--token` -> list all sensors
- `v2_get_node.py`: `--token` `--node_id` -> specific sensor details
- `v2_update_node.py`: `--token` `--node_id` `--payload` (JSON string) -> update node

### Samples (History)
- `v2_get_node_samples.py`: `--token` `--node_id` [`--begin_time`] [`--end_time`] [`--limit`] [`--offset`] -> sensor data
- Model support note: the live API may reject unsupported models such as `ST1`, `ST2`, `ST3`, `ST4`, `ST7`, and `ST8` with `NotSupportResourceException`
- Backward compatibility: `--start` and `--end` are accepted as aliases for `--begin_time` and `--end_time`

### Alerts
- `v2_list_alerts.py`: `--token` [`--limit`] [`--offset`] [`--dismissed`] [`--begin_time`] [`--end_time`] -> list alerts
- `v2_dismiss_all_alerts.py`: `--token` -> dismiss all alerts

## Example Workflow

```bash
# Login - outputs full OAuth JSON
TOKEN=$(python skills/mocreo-sensor-system/scripts/v2_login.py | python -c "import sys,json; print(json.load(sys.stdin)['data']['accessToken'])")
REFRESH=$(python skills/mocreo-sensor-system/scripts/v2_login.py | python -c "import sys,json; print(json.load(sys.stdin)['data']['refreshToken'])")

# List all sensor nodes
python skills/mocreo-sensor-system/scripts/v2_list_nodes.py --token "$TOKEN"

# Get last 10 samples for a node
python skills/mocreo-sensor-system/scripts/v2_get_node_samples.py --token "$TOKEN" --node_id <NODE_ID> --limit 10

# List and dismiss all alerts
python skills/mocreo-sensor-system/scripts/v2_list_alerts.py --token "$TOKEN"
python skills/mocreo-sensor-system/scripts/v2_dismiss_all_alerts.py --token "$TOKEN"

# Refresh when token expires (do this automatically, don't ask the user)
TOKEN=$(python skills/mocreo-sensor-system/scripts/v2_refresh_token.py --refresh_token "$REFRESH" | python -c "import sys,json; print(json.load(sys.stdin)['data']['accessToken'])")
```


