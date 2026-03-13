---
name: mocreo-api
description: MOCREO API toolkit for AI agents. Interact with MOCREO IoT sensors and smart devices via natural language.
version: 1.0.0
tools: [ "run_shell_command" ]
---

# MOCREO API Skills

## First-Time Setup

Before using either sub-skill, check whether shared credentials already exist in the repo-root `.env`.

If `MOCREO_USER`, `MOCREO_PASS`, or `MOCREO_PLATFORM` is missing, run:

```bash
python scripts/bootstrap_credentials.py
```

The bootstrap is the only supported first-run login setup flow:
- It asks guided terminal questions to identify the user's system.
- It uses the following knowledge base:
  - `MOCREO Sensor App` == `MOCREO Sensor System` == `MOCREO V2`
  - `MOCREO Smart App` == `MOCREO Smart System` == `MOCREO V3`
  - V2 hubs: `H1`, `H2`
  - V3 hubs: `H3`, `H5-Lite`, `H5-Pro`, `H6-Lite`, `H6-Pro`
  - V2-only sensors: `ST1`, `ST2`, `ST3`, `ST4`, `ST7`, `ST7-CL`, `SS1`, `NM1`
  - V3-only sensors: `MS2`, `LS1`, `LS2`, `LS3`, `LW1`, `LD1`, `LB1`, `NS1`, `NS2`, `NS3`
  - Shared sensors requiring a follow-up question: `ST5`, `ST6`, `ST8`, `ST9`, `ST10`, `MS1`, `SW2`
- It prompts for the account and password in the terminal, not in chat.
- Password input is hidden via terminal secure entry and then stored locally in `.env`.

Never ask the user to send their password in chat. Never guess their platform.

## Routing - Which Sub-Skill to Load

Read the user's request and load the appropriate sub-skill SKILL.md:

| User mentions | Load |
|---|---|
| "sensor", "hub", "node", "alert", "Sensor System" | `mocreo-sensor-system/SKILL.md` |
| "H5Pro", "H6Pro", "NS1", "NS2", "NS3", "asset", "API key", "Smart System" | `mocreo-smart-system/SKILL.md` |

If the system cannot be determined from the request but credentials are already configured, prefer the saved `MOCREO_PLATFORM`.

If the system cannot be determined and credentials are not configured yet, run the bootstrap flow above instead of asking for free-form credential details in chat.

Once you identify the correct sub-skill, read its SKILL.md and follow the instructions there.

## Repository Layout

```
skills/
|- SKILL.md                       <- this file (router)
|- README.md                      <- human-facing product page
|- requirements.txt               <- shared Python dependencies
|- .env.example                   <- credential template
|- scripts/
|  |- bootstrap_credentials.py    <- interactive shared credential setup
|- common/
|  |- mocreo_auth.py              <- shared credential and platform helpers
|- mocreo-sensor-system/
|  |- SKILL.md                    <- Sensor System instructions for AI
|  \- scripts/                   <- 11 atomic Python scripts
\- mocreo-smart-system/
   |- SKILL.md                    <- Smart System instructions for AI
   \- scripts/                   <- 15 atomic Python scripts
```
