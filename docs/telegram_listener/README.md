# TelegramListenerAgent

## Purpose & Scope
TelegramListenerAgent monitors specified Telegram channels for new messages and processes them through a data pipeline. It provides real-time message listening with automatic reconnection capabilities.

## Prerequisites
- Python 3.10+
- Telethon library
- FastAPI
- Ray Serve
- Stable internet connection

### Required Environment Variables
- `TELEGRAM_PHONE_NUMBER` - Your Telegram account phone number
- `TARGET_CHAT_ID` - ID of the Telegram chat/channel to monitor

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install telethon fastapi ray[serve] python-dotenv
   ```

2. **Set environment variables:**
   ```bash
   export TELEGRAM_PHONE_NUMBER="your_phone_number"
   export TARGET_CHAT_ID="target_chat_id"
   ```

3. **Run the agent:**
   ```bash
   ray start --head
   python -m telegram_listener_agent
   ```

4. **Control the agent:**
   ```bash
   # Start listening
   curl -X POST http://localhost:8000/control/start

   # Check status
   curl http://localhost:8000/control/status

   # Stop listening
   curl -X POST http://localhost:8000/control/stop
   ```

**The agent will:**
- Connect to Telegram servers
- Listen for new messages in specified chat
- Process messages through data pipeline
- Handle connection drops automatically
- Provide status via REST API
