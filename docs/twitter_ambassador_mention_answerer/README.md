# TwitterMentionsAnswerer

## Purpose & Scope
TwitterMentionsMonitor is an autonomous agent that:
- Monitors and responds to Twitter mentions in real-time
- Analyzes conversation context before replying
- Maintains natural response timing to avoid spam detection

## Prerequisites
- Python 3.10+
- Twitter API v2 credentials with read/write permissions
- Redis for tracking responded mentions
- OpenAI API for generating context-aware replies

### Required Environment Variables
- `TWITTER_API_KEY` - Twitter developer API key
- `TWITTER_API_SECRET` - Twitter developer API secret  
- `OPENAI_API_KEY` - For generating intelligent replies
- `REDIS_URL` - Redis connection string (default: redis://localhost:6379)

## Quickstart
1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
export TWITTER_API_KEY="your_key"
export TWITTER_API_SECRET="your_secret"
export OPENAI_API_KEY="your_openai_key"
```

3. **Run the agent:**
```bash
python -m twitter_mentions_monitor.main
```

4. **Start monitoring mentions:**
```bash
curl -X POST http://localhost:8000/yourusername.keywords.hashtags
```
Where:
- `yourusername` = Twitter handle to monitor
- `keywords` = comma-separated terms to track
- `hashtags` = comma-separated relevant hashtags