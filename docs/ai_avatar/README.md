# AIAvatar

## Purpose & Scope
AIAvatar is a Telegram bot that uses the OpenAI API to provide conversational responses, adapting to the user's messaging style by analyzing their recent messages and storing context in Redis.

## Prerequisites
- Python 3.10+
- Telegram API credentials (API_ID and API_HASH from my.telegram.org)
- OpenAI API key for conversational responses
- Redis database for storing user message context
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `API_ID` — Telegram API ID
- `API_HASH` — Telegram API Hash
- `OPENAI_API_KEY` — OpenAI API key for accessing the conversational model
- Redis host credentials (used by `RedisDB`)

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set environment variables:**
   ```bash
   export API_ID="your-telegram-api-id"
   export API_HASH="your-telegram-api-hash"
   export OPENAI_API_KEY="your-openai-api-key"
   export REDIS_HOST="your-redis-host"
   export REDIS_PORT="your-redis-port"
   export REDIS_DB="0"
   ```
3. **Run the bot:**
   ```bash
   python ai_avatar/main.py
   ```
4. **Authenticate and interact:**
   - Follow prompts to enter phone number and SMS code (or password if 2FA is enabled).
   - In Telegram, send messages to the bot or use `/new_style` to refresh the user’s messaging style context.

**The bot will:**
- Authenticate with Telegram using Telethon
- Fetch up to 100 recent user messages for style analysis
- Generate responses via OpenAI, adapting to the user’s tone and style
- Store the latest response in Redis for contextual continuity
