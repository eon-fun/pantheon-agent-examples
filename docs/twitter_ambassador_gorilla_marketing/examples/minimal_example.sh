#!/bin/bash
API_BASE="http://localhost:8000/gorilla-marketing"

# 1. Basic campaign with default settings
echo "Starting basic campaign..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  "$API_BASE/cryptodev.defi,web3.crypto,blockchain" | jq

# Expected response:
# {
#   "status": "completed",
#   "account": "cryptodev",
#   "comments_posted": 2,
#   "last_tweet_id": "1784140326827733400"
# }

# 2. Error case (invalid goal format)
echo -e "\nTesting error handling..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{}' \
  "$API_BASE/invalid_goal_format" | jq

# Environment variables needed:
# export TWITTER_BEARER_TOKEN="your_twitter_token"
# export OPENAI_API_KEY="your_openai_key"
# export REDIS_URL="redis://localhost:6379"