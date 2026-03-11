# MOCREO API Skills

Let your AI agent operate MOCREO devices directly, using plain language.

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

Credentials are stored in a local `.env` file (git-ignored). AI agents are explicitly instructed never to guess credentials or request passwords in chat.

## License

MIT
