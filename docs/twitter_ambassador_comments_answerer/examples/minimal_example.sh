#!/bin/bash
# TwitterAmbassadorCommentsAnswerer - Basic Interaction Examples

# 1. Engage with project comments
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"goal":"your_bot.nfinity_io.web3,ai.decentralization"}' \
  http://localhost:8000/

# Expected response format:
# {
#   "status": "engaged",
#   "comments_processed": 5,
#   "replies_posted": 2,
#   "new_comment_ids": ["1786604234150453248", "1786604234150453249"],
#   "content_samples": [
#     "Great point about decentralization - the NFINITY protocol actually...",
#     "The AI components you mentioned are handled by our..."
#   ]
# }
