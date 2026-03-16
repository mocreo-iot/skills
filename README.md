# MOCREO API Skills

Let your AI agent operate MOCREO devices directly, using plain language.

## Install

**Option 1 — Claude Code plugin marketplace:**

```bash
/plugin marketplace add mocreo-iot/skills
```

Or install a specific version by package name:

```bash
/plugin install mocreo-skills@1.0.0
```

**Option 2 — npx (skills.sh):**

```bash
npx skills add mocreo-iot/skills
```

Both methods install the root `mocreo-api` skill, which acts as a router for the two system-specific skills in this repo:

- `mocreo-sensor-system`
- `mocreo-smart-system`

After installation, ask naturally for the task you want. The root skill will route to the correct sub-skill based on whether your request is about the MOCREO Sensor System or the MOCREO Smart System.

## First Login Setup

On first use, run:

```bash
python scripts/setup_credentials.py
```

The bootstrap flow avoids manual `.env` editing:
- It asks guided terminal questions about the app, Hub, or Sensor model to determine whether you are on Sensor System (V2) or Smart System (V3).
- It then asks for your MOCREO account and password directly in the terminal.
- Password input is hidden and the values are saved only to the local git-ignored `.env` file.

Shared configuration uses:

```env
MOCREO_USER=your_email@example.com
MOCREO_PASS=your_password
MOCREO_PLATFORM=sensor_or_smart
```

For Smart System API keys, the skill now also keeps a local asset-scoped registry in `.mocreo_v3_apikeys.json` so one account can retain separate read/write keys for multiple assets without overwriting a single global key. This file is created automatically the first time a Smart System API key is saved.

## What You Can Ask

**Device Health**
> "Check the battery level of all my devices and list any below 20%."
> "Which sensors have been offline for more than an hour today?"
> "Give me a full status report for all devices right now."

**Data & History**
> "Export last week's temperature and humidity data from the office sensor to my email."
> "Show me the temperature trend for the cold storage sensor over the past 24 hours."
> "Compare temperature readings between Warehouse A and Warehouse B for last week."

**Device Management**
> "Rename all sensors by zone, using the format 'Zone-Number'."
> "Create a read-only API key for the [Home/Asset Name]."
> "Dismiss all pending alerts."

**Automation**
> "Check every morning if any devices are offline and notify me if so."
> "If any device's temperature exceeds 30 degrees, list them and alert me."
> "Generate a weekly status summary for all devices."

## Supported Systems

| System | Devices |
|--------|---------|
| MOCREO Sensor System | Sensor nodes, hubs, alert management |
| MOCREO Smart System | H5Pro, H6Pro, NS1 / NS2 / NS3 |

## Privacy

Credentials are stored only in the local `.env` file (git-ignored). The setup flow uses hidden terminal password entry, and AI agents are instructed never to guess credentials or request passwords in chat.

## License

MIT

