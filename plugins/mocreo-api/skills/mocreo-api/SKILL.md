---
name: mocreo-api
description: MOCREO English device-data router for battery, temperature, humidity, online status, alerts, and history queries by device ID, node ID, asset, or hub across Smart System (V3) and Sensor System (V2).
version: 1.0.5
tools: [ "run_shell_command" ]
---

# MOCREO API Skills

This is the root router skill. Load this skill first, then route to exactly one sub-skill.

Use this skill whenever the user is asking about a MOCREO device's battery, temperature, humidity, online status, alerts, or history, including English requests that only provide a device ID, node ID, SN, asset, or hub model without explicitly saying MOCREO.


## First-Time Setup

Do not proactively read or inspect the `.env` file. Credentials are checked automatically when the login script runs. If either `v2_login.py` or `v3_login.py` exits with code `2` and stderr contains `MOCREO_CREDENTIALS_MISSING`, output the following message **verbatim** — do not summarize, rephrase, or shorten it. Then stop and wait for the user to confirm setup is complete before taking any further action.

### Credential Missing — Fixed Response

---

MOCREO credentials are not configured. Open a terminal, navigate to the runtime root, and run the setup script:

**macOS / Linux / Windows**
```bash
python scripts/setup_credentials.py
```

The script will guide you through platform selection and prompt for your email and password (password input is hidden). Let me know once it's done and I will continue.

---

If the login script does find credentials but the login still fails, do not say setup is missing. Treat that as a configured-but-invalid state: the saved account, password, or selected platform is likely wrong. In that case, tell the user that the bootstrap may have saved credentials without proving they work, ask them to rerun the setup and confirm they picked the correct platform, and only mention platform mismatch as a possibility rather than a certainty.

**Do NOT run `setup_credentials.py` or any login script yourself.** They require interactive terminal input (platform menus, hidden password) and will hang in a non-interactive AI shell.

The setup flow:
- It asks guided terminal questions to identify the user's system.
- It uses the following knowledge base:
  - `MOCREO Sensor App` == `MOCREO Sensor System` == `MOCREO V2`
  - `MOCREO Smart App` == `MOCREO Smart System` == `MOCREO V3`
  - V2 hubs: `H1`, `H2`
  - V3 hubs: `H3`, `H5-Lite`, `H5-Pro`, `H6-Lite`, `H6-Pro`
  - V2-only sensors: `ST1`, `ST2`, `ST3`, `ST4`, `ST7`, `ST7-CL`, `SS1`, `NM1`
  - V3-only sensors: `MS2`, `LS1`, `LS2`, `LS3`, `LW1`, `LD1`, `LB1`, `NS1`, `NS2`, `NS3`
  - Shared sensors requiring a follow-up question: `ST5`, `ST6`, `ST8`, `ST9`, `ST10`, `MS1`, `SW2`
- Password input is hidden via terminal secure entry and stored only in the local `.env` file.
- In Claude marketplace deployments, shared runtime files such as `.env` and `.mocreo_v3_apikeys.json` live at the marketplace root rather than inside `plugins/mocreo-api`.

Never ask the user to send their password in chat. Never guess their platform.
Never install Python dependencies without the user's permission. If a missing-package error appears, explain the install command first, warn when it may affect the current or global Python environment, and wait for approval before running it.

## Routing - Which Sub-Skill to Load

Read the user's request and load the appropriate sub-skill SKILL.md:

| User mentions | Load |
|---|---|
| "MOCREO Sensor App", "Sensor System", "V2", "H1", "H2", "node", "alert" | Source / npx: `mocreo-sensor-system/SKILL.md`  Claude marketplace: `skills/mocreo-sensor-system/SKILL.md` |
| "MOCREO Smart App", "Smart System", "V3", "H3", "H5", "H6", "NS1", "NS2", "NS3", "asset", "API key" | Source / npx: `mocreo-smart-system/SKILL.md`  Claude marketplace: `skills/mocreo-smart-system/SKILL.md` |

Routing priority:
- If `setup_credentials.py` has already saved `MOCREO_PLATFORM`, treat that saved platform as the primary source of truth.
- Do not override the saved platform just because the user says generic words like `sensor`, `temperature`, `humidity`, `monitoring data`, or `device data`.
- The word `sensor` alone is not enough to choose `mocreo-sensor-system`, because both Smart System and Sensor System can include sensors.
- Only use request keywords as a routing hint when the request includes system-specific evidence such as app name, hub family, explicit system name, or clearly system-bound entities like `asset` or `API key`.

If the system cannot be determined from the request but credentials are already configured, use the saved `MOCREO_PLATFORM`.

If the system cannot be determined and credentials are not configured yet, output the fixed "Credential Missing" response above instead of asking for free-form credential details in chat.

Once you identify the correct sub-skill, read its SKILL.md and follow the instructions there.

## Before Every Shell Command

Before running any script, always output one short sentence in plain language explaining what you are about to do and why. Keep it under 15 words. Do this every time, without exception — it helps the user understand the permission prompt and feel confident approving it.

Examples:
- Logging in to get an access token.
- Fetching the list of sensors under your account.
- Checking existing API keys on Home/Asset before creating a new one.
- Deleting unused key `testexamples123` from Home/Asset as confirmed.

Never use technical jargon (no "Bearer token", no "exit code", no script names) in this sentence.

## Command Base Path

Run all commands from the runtime root shown below, not from an individual sub-skill folder. Use the path variant that exists in the current install:

- Source repo or `npx skills add`: `python scripts/setup_credentials.py` or `python mocreo-smart-system/scripts/v3_login.py`
- Claude marketplace package: `python scripts/setup_credentials.py` or `python skills/mocreo-smart-system/scripts/v3_login.py`

## Runtime Layout

The runtime root for this skill should contain the files needed to execute commands directly.

Source repo and `npx skills add` layout:

```
runtime-root/
|- SKILL.md                      <- this file (router)
|- requirements.txt              <- shared Python dependencies
|- scripts/
|  \- setup_credentials.py       <- interactive shared credential setup (Python)
|- common/
|  \- mocreo_auth.py             <- shared credential and platform helpers
|- mocreo-sensor-system/
|  |- SKILL.md                   <- Sensor System instructions for AI
|  \- scripts/                   <- Sensor System Python scripts
|- mocreo-smart-system/
|  |- SKILL.md                   <- Smart System instructions for AI
|  \- scripts/                   <- Smart System Python scripts
|- openapi.en.yaml               <- Smart System OpenAPI reference
|- openapi.zh.yaml               <- Smart System OpenAPI reference (Chinese)
\- sensor-swagger.json          <- Sensor System Swagger reference
```

Claude marketplace package layout:

```
runtime-root/
|- .claude-plugin/
|  \- plugin.json                <- plugin manifest when packaged for Claude
|- requirements.txt
|- scripts/
|- common/
|- skills/
|  |- mocreo-api/
|  |  \- SKILL.md                <- this file (router)
|  |- mocreo-sensor-system/
|  |  |- SKILL.md
|  |  \- scripts/
|  \- mocreo-smart-system/
|     |- SKILL.md
|     \- scripts/
|- openapi.en.yaml
|- openapi.zh.yaml
\- sensor-swagger.json
```

In the canonical source repository, the Claude marketplace manifest lives at `.claude-plugin/marketplace.json`, and the self-contained Claude plugin package is generated under `plugins/mocreo-api/`. In Claude marketplace deployments, the shared `.env`, `.env.example`, and `.mocreo_v3_apikeys.json` live at the marketplace root outside the nested plugin folder.



