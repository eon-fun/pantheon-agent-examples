#!/bin/bash

# Example: Find DeFi pools for USDC token
# Input: Token address for USDC on Ethereum (chainId=1)

curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "YOUR_CHAT_ID", "text": "/find_pools 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"}' \
  https://api.telegram.org/botYOUR_TELEGRAM_BOT_TOKEN/sendMessage

# Expected Output (sent to Telegram chat):
#
#🏆 *Finded pools for investment:*
#
#• *ProtocolA*:
#  - APY: 5.20%
#  - Pool type: staking
#  - Contract: `0x...`
#
#📊 *Description of best pool:*
#- Protocol: ProtocolA
#- APY: 5.20%
#- Type: `staking`
#- Pool address: `0x...`
#- Contract: `0x...`
#
#💰 *Tokens in pool:*
#    - USDC: $1.00
#    - ETH: $3,500.00