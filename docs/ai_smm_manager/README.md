# NewsAggregatorBot

## Purpose & Scope
NewsAggregatorBot is an AI-powered content aggregation and publishing system that:
- Monitors news websites for cryptocurrency articles
- Tracks Twitter accounts for relevant tweets
- Processes content through AI for summarization/rewriting
- Publishes formatted posts to Telegram channels

## Prerequisites
- Python 3.10+
- Redis server
- Telegram bot token
- Twitter API v2 access
- OpenAI/Grok API access
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `TELEGRAM_BOT_TOKEN` - Telegram bot authentication
- `TELEGRAM_CHANNEL_ID` - Target channel ID
- `TWITTER_BEARER_TOKEN` - Twitter API v2 bearer token
- `GROK_API_KEY` - xAI Grok API key
- `REDIS_URL` - Redis connection string

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token"
   export TWITTER_BEARER_TOKEN="your_twitter_token"
   ```

3. **Run the bot:**
   ```bash
   python news_aggregator_bot.py
   ```

4. **Add sources:**
   ```
   /add_links https://cointelegraph.com
   /add_x_account elonmusk
   ```

**Key Features:**
- Multi-source aggregation
- AI content processing
- Rate-limited publishing
- Duplicate prevention
