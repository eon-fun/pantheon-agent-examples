# AiTwitterSummary

## Purpose & Scope
TweetProcessor is an AI-powered Twitter monitoring system that:
- Tracks specified Twitter accounts for new tweets
- Generates concise AI summaries of tweet content
- Publishes formatted summaries to Telegram channels
- Maintains state of processed tweets

## Prerequisites
- Python 3.10+
- Ray framework
- Redis server
- Twitter API v2 access
- OpenAI API access
- Telegram bot token
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `TELEGRAM_BOT_TOKEN` - Telegram bot authentication
- `TELEGRAM_CHANNEL_ID` - Target channel ID
- `TWITTER_BEARER_TOKEN` - Twitter API v2 bearer token
- `OPENAI_API_KEY` - OpenAI API key
- `REDIS_URL` - Redis connection string

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Ray:**
   ```bash
   ray start --head
   ```

3. **Run the processor:**
   ```bash
   python tweet_processor.py
   ```

4. **Add accounts to monitor:**
   ```python
   # Add to Redis set
   redis_client.sadd("subscribed_twitter_accounts", "elonmusk")
   ```

**Key Features:**
- Real-time tweet monitoring
- AI-powered summarization
- HTML-formatted Telegram posts
- Duplicate prevention
- Error-resilient operation
