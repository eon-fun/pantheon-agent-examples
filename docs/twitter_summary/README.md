# TweeterSummary

## Purpose & Scope
TweetProcessor automates Twitter content monitoring and summarization by:
- Tracking specified Twitter accounts
- Fetching new tweets periodically
- Generating AI-powered summaries
- Delivering summaries to Telegram channels

## Prerequisites
- Python 3.10+
- Twitter API v2 credentials
- OpenAI API access
- Redis for state management
- Telegram bot token
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `TWITTER_BEARER_TOKEN` - Twitter API bearer token
- `OPENAI_API_KEY` - OpenAI API key
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `TELEGRAM_CHANNEL_ID` - Target channel ID
- `REDIS_URL` - Redis connection string

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export TWITTER_BEARER_TOKEN="your_twitter_token"
   export OPENAI_API_KEY="your_openai_key"
   export TELEGRAM_BOT_TOKEN="your_telegram_token"
   ```

3. **Run the agent:**
   ```bash
   serve run tweet_processor:app
   ```

4. **Add accounts to monitor:**
   ```bash
   curl -X POST "http://localhost:8000/add_account" \
   -H "Content-Type: application/json" \
   -d '{"account": "twitterhandle"}'
   ```

**Key Features:**
- 6-hour monitoring intervals
- AI-powered summarization
- Duplicate detection
- HTML-formatted Telegram output
