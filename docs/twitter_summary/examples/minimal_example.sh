#!/bin/bash
# TweetProcessor - Usage Examples

# 1. Add account to monitor
curl -X POST "http://localhost:8000/add_account" \
  -H "Content-Type: application/json" \
  -d '{"account": "elonmusk"}'

# 2. Example Telegram output format
echo "Sample Telegram Output:"
echo "<b>Twitter Summary Report</b>"
echo "<i>Generated: $(date)</i>"
echo ""
echo "🐦 <b>@elonmusk</b>:"
echo "• Discussed new AI initiatives..."
echo "• Announced Tesla updates..."
echo ""
echo "📊 <i>3 tweets analyzed</i>"
