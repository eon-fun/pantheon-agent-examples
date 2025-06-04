#!/bin/bash
# NewsAggregatorBot - Usage Examples

# 1. Add news sources
curl -X POST "http://localhost:8000/add_links" \
  -H "Content-Type: application/json" \
  -d '["https://cointelegraph.com", "https://decrypt.co"]'

# 2. Add Twitter accounts
curl -X POST "http://localhost:8000/add_x_account" \
  -H "Content-Type: application/json" \
  -d '["elonmusk", "cz_binance"]'

# 3. Sample AI-processed output
echo "Sample Telegram Post:"
echo "🚀 **Major Bitcoin Rally**"
echo ""
echo "BTC surged 15% today amid ETF approval rumors..."
echo ""
echo "*Key points:*"
echo "- ETF decision expected Friday"
echo "- Institutional inflows up 300%"
echo "- Resistance at 45K"
echo ""
echo "#Bitcoin #Crypto #ETF"