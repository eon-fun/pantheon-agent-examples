# DialogueManager

## Purpose & Scope
DialogueManager is a conversation processing system that:
- Monitors and processes messages from Telegram chats
- Generates AI-powered summaries of conversations
- Tracks read/unread messages
- Provides command-based interaction (/summary)

## Prerequisites
- Python 3.10+
- Ray framework
- Redis server
- Telegram API access (Telethon)
- OpenAI API access
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `TELEGRAM_API_ID` - Telegram API ID
- `TELEGRAM_API_HASH` - Telegram API hash
- `OPENAI_API_KEY` - OpenAI API key
- `REDIS_URL` - Redis connection string

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   export TELEGRAM_API_ID="your_api_id"
   export TELEGRAM_API_HASH="your_api_hash"
   ```

3. **Run the manager:**
   ```bash
   serve run dialogue_manager:app
   ```

4. **Interact via Telegram:**
   ```
   /summary - Generate conversation summary
   ```

**Key Features:**
- Real-time message processing
- Context-aware summarization
- Read state tracking
- Command-based interaction
