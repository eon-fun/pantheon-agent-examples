#!/bin/bash
# AI Avatar - Basic Interaction Example

# 1. Start conversation
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "USER_CHAT_ID", "text": "Hello"}' \
  https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage

# 2. Expected response format:
# {
#   "ok": true,
#   "result": {
#     "text": "Hi there! *adjusts tone to match your style* How can I help?",
#     "reply_markup": {"remove_keyboard": true}
#   }
# }

# 3. Refresh user style (manual update)
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "USER_CHAT_ID", "text": "/new_style"}' \
  https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage

# Environment variables needed:
# export TELEGRAM_BOT_TOKEN="your_bot_token"
# export OPENAI_API_KEY="your_openai_key"