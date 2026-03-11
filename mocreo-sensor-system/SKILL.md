---
name: mocreo-sensor-system
description: MOCREO Sensor System skill. Supports hubs, sensor nodes, alerts, and monitoring via modular atomic scripts.
version: 1.0.0
tools: [ "run_shell_command" ]
---

# MOCREO Sensor System Skill

## Triggering
- When users ask to query MOCREO Sensor System data.
- When users ask to manage devices (hubs), nodes (sensors), or alerts.

## Environment (AI Handles Automatically)

**Dependencies**: If a script fails with `ModuleNotFoundError`, auto-run from repo root:
```bash
pip install -r requirements.txt
```
Try `pip3` or `python -m pip install requests python-dotenv` if that fails. Never ask the user to install packages.

**Credentials**:
1. Check if `.env` exists at the repo root (`../../.env` relative to `scripts/`).
2. If missing: tell the user their credentials will be saved locally, ask for email and password, then create `.env` yourself using your file-writing tool. Use variables `MOCREO_V2_USER` and `MOCREO_V2_PASS`.
3. Never guess credentials. Never ask for them again in chat once saved.
4. If login returns 401: tell the user their credentials look wrong and ask them to update `.env` directly — do not ask them to type the password in chat.

**Token lifecycle**:
1. After login, save both `access_token` and `refresh_token` from the JSON output.
2. If any API call returns 401: automatically run `scripts/v2_refresh_token.py` with the saved refresh token, then retry the original call.
3. If refresh also fails: inform the user the session has expired and re-run login.

## Output Contract
- **stdout**: JSON data on success (parse this for chaining)
- **stderr**: Error messages only
- **exit code**: `0` = success, `1` = failure

## Script Location
All scripts are in `scripts/`. Always run from the skill root:
```bash
python scripts/v2_login.py [args]
```

## Instructions
1. **Architecture**: Uses username/password to get an OAuth token, then passes that token as a Bearer header on all subsequent calls.
2. **Standard Flow**:
   - Login → get token
   - List devices (`v2_list_devices.py`) or nodes (`v2_list_nodes.py`) to find IDs
   - Use IDs for specific operations (samples, alerts, etc.)

## Available Scripts (11)

### Auth & User
- `v2_login.py`: `--username` `--password` → full OAuth JSON (access_token + refresh_token)
- `v2_refresh_token.py`: `--refresh_token` → new token JSON
- `v2_get_user.py`: `--token` → current user info

### Devices (Hubs)
- `v2_list_devices.py`: `--token` → list all hubs
- `v2_get_device.py`: `--token` `--sn` → specific hub details

### Nodes (Sensors)
- `v2_list_nodes.py`: `--token` → list all sensors
- `v2_get_node.py`: `--token` `--node_id` → specific sensor details
- `v2_update_node.py`: `--token` `--node_id` `--payload` (JSON string) → update node

### Samples (History)
- `v2_get_node_samples.py`: `--token` `--node_id` [`--start`] [`--end`] [`--limit`] → sensor data

### Alerts
- `v2_list_alerts.py`: `--token` → list alerts
- `v2_dismiss_all_alerts.py`: `--token` → dismiss all alerts

## Example Workflow

```bash
# Login — outputs full OAuth JSON
TOKEN=$(python scripts/v2_login.py | python -c "import sys,json; print(json.load(sys.stdin)['data']['accessToken'])")
REFRESH=$(python scripts/v2_login.py | python -c "import sys,json; print(json.load(sys.stdin)['data']['refreshToken'])")

# List all sensor nodes
python scripts/v2_list_nodes.py --token "$TOKEN"

# Get last 10 samples for a node
python scripts/v2_get_node_samples.py --token "$TOKEN" --node_id <NODE_ID> --limit 10

# List and dismiss all alerts
python scripts/v2_list_alerts.py --token "$TOKEN"
python scripts/v2_dismiss_all_alerts.py --token "$TOKEN"

# Refresh when token expires (do this automatically, don't ask the user)
TOKEN=$(python scripts/v2_refresh_token.py --refresh_token "$REFRESH" | python -c "import sys,json; print(json.load(sys.stdin)['data']['accessToken'])")
```
