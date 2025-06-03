# APYAgent

## Purpose & Scope
APYAgent is a Telegram bot that interacts with the Enso Finance API to find and recommend secure DeFi investment pools for a specified token, ensuring safe and high-yield opportunities.

## Prerequisites
- Python 3.10+
- Telegram Bot Token (obtained from BotFather)
- Enso Finance API key
- Redis is not required, but a stable internet connection is needed for API requests
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `TELEGRAM_BOT_TOKEN` — Telegram Bot API token
- `ENSO_API_KEY` — Enso Finance API key for accessing DeFi data

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set environment variables:**
   ```bash
   export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
   export ENSO_API_KEY="your-enso-api-key"
   ```
3. **Run the bot:**
   ```bash
   python apy_agent/main.py
   ```
4. **Interact with the bot in Telegram:**
   - Start the bot with `/start`
   - Find pools with `/find_pools <token_address>`, e.g.:
     ```bash
     /find_pools 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
     ```

**The agent will:**
- Authenticate with the Enso Finance API
- Retrieve a list of supported protocols and DeFi tokens
- Identify safe pools with valid APY (0.1%–100%) for the specified token
- Return a formatted recommendation with pool details in Telegram