#!/bin/bash
# APYAgent - Usage Examples

# 1. Find pools for USDC
curl -X POST "http://localhost:8000/find_pools" \
  -H "Content-Type: application/json" \
  -d '{"token_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"}'

# 2. Find pools for DAI
curl -X POST "http://localhost:8000/find_pools" \
  -H "Content-Type: application/json" \
  -d '{"token_address": "0x6B175474E89094C44Da98b954EedeAC495271d0F"}'

# 3. Telegram command example
echo "Simulating Telegram command:"
echo "/find_pools 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

# Expected output format:
# 🏆 Found pools for USDC:
# • ProtocolA:
#   - APY: 5.2%
#   - Type: lending
#   - Contract: 0x...
#
# 💰 Token prices:
#    - USDC: $1.00
#    - ETH: $3,500.00