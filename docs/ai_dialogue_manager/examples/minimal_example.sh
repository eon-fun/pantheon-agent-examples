#!/bin/bash
# Telegram Summarizer - End-to-End Example

# 1. Launch the agent (in background)
python telegram_summarizer/main.py &

# 2. Simulate receiving messages (via Telegram API)
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "YOUR_CHAT_ID",
    "text": "Test message for summarization",
    "unread": true
  }' \
  https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage

# 3. Trigger summary generation
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "YOUR_CHAT_ID",
    "text": "/summary"
  }' \
  https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage

# Expected Output Example:
# {
#   "ok": true,
#   "result": {
#     "text": "📋 Summary:\n\n[Test Chat] @user1 mentioned: Need help with project\n[Work Group] @boss replied: Deadline extended",
#     "parse_mode": "Markdown"
#   }
# }

# Environment Variables Required:
# export TELEGRAM_BOT_TOKEN="your_bot_token"
# export API_ID="your_telegram_api_id"
# export API_HASH="your_telegram_api_hash"
# export OPENAI_API_KEY="your_openai_key"