# MOCREO API Skills for Gemini CLI

This repository contains specialized Gemini CLI Skills designed to interact securely with MOCREO systems. It is divided into two distinct skill packages:

1. **`mocreo-v2-api`**: For the MOCREO Sensor System (OAuth-based token authentication).
2. **`mocreo-v3-api`**: For the MOCREO Smart System (Dual authentication via OAuth Token & API Key).

## Features
- **Privacy First**: Credentials are kept locally in a `.env` file at the root of the repository. The AI is specifically instructed never to guess or expose them.
- **AI Guided Setup**: Activate either skill, and the AI will guide you through the secure local setup.
- **Atomic Tooling**: All scripts are modular and can be used statelessly by AI agents or external cron jobs.

## Installation

1. Clone this repository:
   ```bash
   git clone <your-github-repo-url> mocreo-api-skills
   ```
2. Install the required global Python packages:
   ```bash
   cd mocreo-api-skills
   pip install -r requirements.txt
   ```
3. Link or install the skills into your Gemini CLI environment:
   ```bash
   gemini skills install ./mocreo-v2-api
   gemini skills install ./mocreo-v3-api
   ```

## Configuration

We use a single `.env` file at the root of this project to store credentials securely (this file is git-ignored). Python's `dotenv` package will automatically find it.

Copy the example file and fill in your details:
```bash
cp .env.example .env
```

Then edit `.env`:
```env
# V2 System
MOCREO_V2_USER=your_email@example.com
MOCREO_V2_PASS=your_password

# V3 System
MOCREO_V3_EMAIL=your_email@example.com
MOCREO_V3_PASS=your_password
MOCREO_V3_API_KEY=your_api_key
```

## Usage

In your Gemini CLI session, simply ask the AI to perform tasks based on the skill you need:

> "Use the mocreo-v2-api skill to list my hubs."
> 
> "Use the mocreo-v3-api skill to check the battery of my devices using my API key."