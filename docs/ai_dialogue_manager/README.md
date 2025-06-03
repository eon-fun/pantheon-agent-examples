# Telegram Summarizer Agent

## Purpose & Scope
The Telegram Summarizer collects and summarizes unread messages, mentions, and replies across all your Telegram chats. It generates concise daily/weekly digests using OpenAI's API.

## Prerequisites
- Python 3.10+
- Telegram API ID and Hash (from my.telegram.org)
- OpenAI API key
- Redis server for message storage
- Telethon library (`pip install telethon`)

### Required Environment Variables
```bash
export API_ID="your_telegram_api_id"
export API_HASH="your_telegram_api_hash"
export OPENAI_API_KEY="your_openai_key"
```

## Quickstart
1. **Install dependencies:**
```bash
pip install telethon redis openai
```

2. **Run the agent:**
```bash
python telegram_summarizer/main.py
```

3. **First-run setup:**
- Enter your phone number when prompted
- Provide the SMS verification code
- Complete 2FA if enabled

4. **Usage:**
- The bot automatically collects:
  - Unread messages
  - Direct mentions (@username)
  - Message replies
- Generate summaries with:
```bash
/summary
```

## Features
- Smart message filtering (only unread/important messages)
- Multi-chat support (groups, channels, DMs)
- Automatic cleanup of read messages
- Context-aware summarization
