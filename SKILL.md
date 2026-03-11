---
name: mocreo-api
description: MOCREO API toolkit for AI agents. Interact with MOCREO IoT sensors and smart devices via natural language.
version: 1.0.0
tools: [ "run_shell_command" ]
---

# MOCREO API Skills

## Routing — Which Sub-Skill to Load

Read the user's request and load the appropriate sub-skill SKILL.md:

| User mentions | Load |
|---|---|
| "sensor", "hub", "node", "alert", "Sensor System" | `mocreo-sensor-system/SKILL.md` |
| "H5Pro", "H6Pro", "NS1", "NS2", "NS3", "asset", "API key", "Smart System" | `mocreo-smart-system/SKILL.md` |

If the system cannot be determined from context, ask:
> "Are you using the MOCREO Sensor System (hubs and sensor nodes) or the MOCREO Smart System (H5Pro / H6Pro / NS series)?"

Once you identify the correct sub-skill, read its SKILL.md and follow the instructions there.

## Repository Layout

```
skills/
├── SKILL.md                       <- this file (router)
├── README.md                      <- human-facing product page
├── requirements.txt               <- shared Python dependencies
├── .env.example                   <- credential template
├── mocreo-sensor-system/
│   ├── SKILL.md                   <- Sensor System instructions for AI
│   └── scripts/                   <- 11 atomic Python scripts
└── mocreo-smart-system/
    ├── SKILL.md                   <- Smart System instructions for AI
    └── scripts/                   <- 15 atomic Python scripts
```
