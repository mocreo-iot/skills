---
name: mocreo-v2-api
description: MOCREO v2 Public API skill for MOCREO Sensor System devices. Supports modular, parameter-driven scripts for auth, listing, and monitoring.
version: 1.0.0
tools: [ "run_shell_command" ]
---

# MOCREO v2 Public API Skill

## Triggering
- When users ask to query MOCREO Sensor System (v2) data.
- When users ask to manage tokens, devices (hubs), nodes (sensors), alerts using MOCREO v2 API.

## Setup Instructions (For AI Agents)
1. If credentials (username, password) are missing from the environment or not provided by the user, **DO NOT** attempt to guess them.
2. Ask the user for their MOCREO v2 credentials (email and password) and explain that they can be saved locally in a `.env` file for future use to protect their privacy.
3. Offer to create the `.env` file for the user automatically using the `write_file` tool once they provide the information. Ensure the variables used are `MOCREO_V2_USER` and `MOCREO_V2_PASS`.
4. **CRITICAL PRIVACY RULE**: If login fails due to incorrect credentials or other reasons, **DO NOT** ask the user to provide their login credentials or any private information directly in the chat. Instead, instruct them to update their `.env` file locally.

## Instructions
1. **Understand Architecture**: v2 API uses username/password to get a token, and uses that token as a Bearer token in the Authorization header.
2. **Standard Workflow**:
   - **Step 1**: Use `v2_login.py` to get the `token`.
   - **Step 2**: Use the token to fetch devices (`v2_list_devices.py`) or nodes (`v2_list_nodes.py`).
   - **Step 3**: Use specific IDs to get node samples, alerts, etc.
3. **Important**: Token expires and should be refreshed if needed using `v2_refresh_token.py`.

## Available Scripts (11 Scripts)

### Auth & User
- `v2_login.py`: Takes `--username` and `--password`, returns oauth token.
- `v2_refresh_token.py`: Takes `--refresh_token` to get a new token.
- `v2_get_user.py`: Takes `--token` to get current user info.

### Devices (Hubs)
- `v2_list_devices.py`: Takes `--token` to list all hubs.
- `v2_get_device.py`: Takes `--token` and `--sn` to get specific hub details.

### Nodes (Sensors)
- `v2_list_nodes.py`: Takes `--token` to list all sensors.
- `v2_get_node.py`: Takes `--token` and `--node_id` to get specific sensor details.
- `v2_update_node.py`: Takes `--token`, `--node_id`, `--payload` (JSON string) to update node.

### Samples (History)
- `v2_get_node_samples.py`: Takes `--token`, `--node_id`, optional `--start`, `--end` to get sensor data.

### Alerts
- `v2_list_alerts.py`: Takes `--token` to list alerts.
- `v2_dismiss_all_alerts.py`: Takes `--token` to dismiss all alerts.

