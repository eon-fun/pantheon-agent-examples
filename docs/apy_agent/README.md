# APYAgent

## Purpose & Scope
APYAgent is a Telegram bot that analyzes DeFi investment opportunities by:
- Finding secure liquidity pools for specified tokens
- Validating pool safety parameters
- Recommending optimal investment options
- Providing detailed pool analytics

## Prerequisites
- Python 3.10+
- Telegram Bot Token
- Enso Finance API access
- Redis (optional for caching)
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `TELEGRAM_BOT_TOKEN` - Bot authentication token
- `ENSO_API_KEY` - Enso Finance API key
- `BASE_URL` - Enso API base URL (default: "https://api.enso.finance")

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export ENSO_API_KEY="your_enso_key"
   ```

3. **Run the agent:**
   ```bash
   serve run apy_agent:app
   ```

4. **Interact via Telegram:**
   ```
   /find_pools 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
   ```

**Key Features:**
- Multi-protocol analysis
- Pool safety validation
- APY-based ranking
- Detailed token analytics
