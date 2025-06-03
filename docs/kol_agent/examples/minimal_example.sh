#!/bin/bash
# KolAgent - Engagement Examples

# 1. Start a quick test raid (0.1 minutes = 6 seconds)
curl -X POST "http://localhost:8000/amplify" \
  -H "Content-Type: application/json" \
  -d '{
    "target_tweet_id": "1719810222222222222",
    "tweet_text": "Check out our revolutionary new AI product! #Innovation",
    "bot_accounts": [
      {
        "username": "tech_bot1",
        "role": "advocate",
        "account_access_token": "token123",
        "user_id": "12345"
      }
    ],
    "raid_minutes": 0.1
  }'

# 2. Check all configured accounts
curl -s "http://localhost:8000/all_accounts" | jq .

# 3. Start multi-account raid
curl -X POST "http://localhost:8000/trending" \
  -H "Content-Type: application/json" \
  -d '{
    "target_tweet_id": "1719810222333333333",
    "tweet_text": "Breaking: Major breakthrough in quantum computing!",
    "bot_accounts": [
      {
        "username": "science_bot1",
        "role": "expert",
        "account_access_token": "token456",
        "user_id": "67890"
      },
      {
        "username": "news_bot2",
        "role": "reporter",
        "account_access_token": "token789",
        "user_id": "13579"
      }
    ],
    "raid_minutes": 5.0
  }'

# Expected error response (invalid token):
# {
#   "success": false,
#   "message": "Failed to authenticate account science_bot1"
# }