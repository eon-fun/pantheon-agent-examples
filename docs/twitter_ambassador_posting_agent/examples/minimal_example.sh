#!/bin/bash
# TwitterPostingAgent - Basic Interaction Examples

# 1. Post regular tweet
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"goal":"cryptodev.defi,web3.crypto,blockchain"}' \
  http://localhost:8000/

# Expected response format:
# {
#   "status": "posted",
#   "tweet_id": "1689264827354624",
#   "content": "DeFi is rebuilding finance from ground up.\n\nWeb3 brings verifiable ownership models.\n\nThe future is decentralized.",
#   "type": "regular"
# }

# 2. Force news summary tweet
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"goal":"newsbot.ethereum,layer2.scaling", "force_type":"news"}' \
  http://localhost:8000/

# 3. Get posting history
curl -s -X GET \
  http://localhost:8000/cryptodev/history

# Environment variables required:
# export TWITTER_API_KEY="your_twitter_key"
# export TWITTER_API_SECRET="your_twitter_secret"
# export OPENAI_API_KEY="your_openai_key"
# export REDIS_URL="redis://localhost:6379"

# Rate limits:
# - Max 3 posts/hour per account
# - 10 concurrent generation processes