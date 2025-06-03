# API & Configuration Reference

## Telegram Commands

### `/find_pools <token_address>`
Finds investment pools for specified ERC-20 token

#### Parameters
- `token_address`: Valid Ethereum token address (e.g., USDC: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`)

#### Responses
Returns Markdown-formatted message with:
- Best pool recommendation
- Top 5 alternatives
- Token price information
- Safety indicators

## Configuration

### Environment Variables
| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | BotFather token |
| `ENSO_API_KEY` | Enso Finance API key |
| `BASE_URL` | Enso API endpoint |

### Safety Thresholds
| Parameter | Value |
|-----------|-------|
| Min APY | 0.1% |
| Max APY | 100% |
| Price Data Age | <24h |
| Min Tokens | 2 |
