# MOCREO API Toolkits for AI Agents

This repository contains specialized scripting toolkits designed to empower AI agents (such as Cursor, GitHub Copilot, Gemini CLI, Claude, ChatGPT, etc.) to interact securely with MOCREO systems. It is divided into two distinct packages:

1. **`mocreo-v2-api`**: For the MOCREO Sensor System (OAuth-based token authentication).
2. **`mocreo-v3-api`**: For the MOCREO Smart System (Dual authentication via OAuth Token & API Key).

## Features
- **Model Agnostic**: Pure Python scripts that can be executed by any AI agent with local terminal access, or run manually via cron jobs.
- **Privacy First**: Credentials are kept locally in a `.env` file at the root of the repository. AI agents are specifically instructed (via `SKILL.md` docs) never to guess or expose them.
- **AI Guided Context**: Each toolkit includes a `SKILL.md` file that acts as a system prompt/instruction manual for the AI, teaching it exactly how to chain the scripts together.
- **Atomic Tooling**: All scripts are modular and stateless.

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone <your-github-repo-url> mocreo-api-skills
   ```
2. Install the required Python packages (creating a virtual environment is recommended):
   ```bash
   cd mocreo-api-skills
   pip install -r requirements.txt
   ```

## Configuration

We use a single `.env` file at the root of this project to store credentials securely (this file is git-ignored). Python's `dotenv` package will automatically load these variables.

Copy the example file and fill in your details:
```bash
cp .env.example .env
```

Then edit `.env` securely in your text editor:
```env
# V2 System
MOCREO_V2_USER=your_email@example.com
MOCREO_V2_PASS=your_password

# V3 System
MOCREO_V3_EMAIL=your_email@example.com
MOCREO_V3_PASS=your_password
MOCREO_V3_API_KEY=your_api_key
```

## Usage with AI Agents

To use these toolkits with your preferred AI assistant:

1. **Open the Project**: Open this repository folder in your AI-powered IDE (like Cursor, Windsurf, or VS Code with Copilot) or point your CLI agent to this directory.
2. **Provide Context**: Ask the AI to read the `SKILL.md` file in the respective folder (`mocreo-v2-api/SKILL.md` or `mocreo-v3-api/SKILL.md`). This gives the AI all the instructions it needs.
3. **Prompt the AI**: Simply ask the AI to perform tasks using natural language.

**Example Prompts:**

> "Read mocreo-v2-api/SKILL.md to understand the workflow, then list all my hubs."
> 
> "Based on the mocreo-v3-api toolkit, check the battery level of my devices using my API key."
>
> "Use the v3 scripts to export the temperature history for yesterday and send it to my email."