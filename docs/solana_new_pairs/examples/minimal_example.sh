#!/bin/bash
# SolanaNewPairsBot - Interaction Examples

# 1. Check service status
curl -s http://localhost:8000/status

# 2. Trigger manual collection (example goal)
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"plan":{"interval":"30s"}}' \
  http://localhost:8000/monitor

# Expected response:
# {"status":"main запущен"}

# 3. Sample Telegram post format
echo '🚀 New SOL Pair: 
Token: 7vf...CxR 
Pool: 5Zg...Q2w 
Liquidity: $12,450'