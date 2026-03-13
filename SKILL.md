---
name: mocreo-api
description: MOCREO API toolkit for AI agents. Interact with MOCREO IoT sensors and smart devices via natural language.
version: 1.0.0
tools: [ "run_shell_command" ]
---

# MOCREO API Skills

## First-Time Setup

Do not proactively read or inspect the `.env` file. Credentials are checked automatically when the login script runs. If either `v2_login.py` or `v3_login.py` exits with code `2` and stderr contains `MOCREO_CREDENTIALS_MISSING`, output the following message **verbatim** — do not summarize, rephrase, or shorten it. Then stop and wait for the user to confirm setup is complete before taking any further action.

### Credential Missing — Fixed Response

---

MOCREO credentials are not configured. Open a terminal, navigate to the skill folder, and run the setup script:

**macOS / Linux**
```bash
bash scripts/mocreo-config.sh
```

**Windows (Command Prompt or PowerShell)**
```powershell
python scripts\bootstrap_credentials.py
```

The script will guide you through platform selection and prompt for your email and password (password input is hidden). Let me know once it's done and I will continue.

---

**Do NOT run `bootstrap_credentials.py`, `mocreo-config.sh`, or any login script yourself.** They require interactive terminal input (platform menus, hidden password) and will hang in a non-interactive AI shell.

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

Never ask the user to send their password in chat. Never guess their platform.

## Routing - Which Sub-Skill to Load

Read the user's request and load the appropriate sub-skill SKILL.md:

| User mentions | Load |
|---|---|
| "sensor", "hub", "node", "alert", "Sensor System" | `mocreo-sensor-system/SKILL.md` |
| "H5Pro", "H6Pro", "NS1", "NS2", "NS3", "asset", "API key", "Smart System" | `mocreo-smart-system/SKILL.md` |

If the system cannot be determined from the request but credentials are already configured, prefer the saved `MOCREO_PLATFORM`.

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

## Repository Layout

```
skills/
|- SKILL.md                       <- this file (router)
|- README.md                      <- human-facing product page
|- requirements.txt               <- shared Python dependencies
|- .env.example                   <- credential template
|- scripts/
|  |- bootstrap_credentials.py    <- interactive shared credential setup (Python)
|  |- mocreo-config.sh            <- shell launcher for bootstrap (entry point for run://mocreo-config)
|- common/
|  |- mocreo_auth.py              <- shared credential and platform helpers
|- mocreo-sensor-system/
|  |- SKILL.md                    <- Sensor System instructions for AI
|  \- scripts/                   <- 11 atomic Python scripts
\- mocreo-smart-system/
   |- SKILL.md                    <- Smart System instructions for AI
   \- scripts/                   <- 15 atomic Python scripts
```
