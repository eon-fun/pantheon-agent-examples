#!/bin/bash
# TwitterMentionsMonitor - Basic Usage Examples

# 1. Start monitoring mentions
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"goal":"cryptodev.defi,web3.crypto,blockchain"}' \
  http://localhost:8000/

# Expected response:
# {
#   "status": "monitoring_started",
#   "account": "cryptodev",
#   "first_check_completed": true,
#   "mentions_found": 2
# }

# 2. Force immediate mention check
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"goal":"newsbot.ethereum,layer2", "force_check":true}' \
  http://localhost:8000/

# 3. Get response history
curl -s -X GET \
  http://localhost:8000/cryptodev/history

# Required environment variables:
# export TWITTER_API_KEY="your_twitter_key"
# export TWITTER_API_SECRET="your_twitter_secret"
# export OPENAI_API_KEY="your_openai_key"
# export REDIS_URL="redis://localhost:6379"