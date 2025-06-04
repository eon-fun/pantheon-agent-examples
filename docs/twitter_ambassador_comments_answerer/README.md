# Twitter Ambassador Comments Answerer

## Purpose & Scope
TwitterAmbassadorCommentsAnswerer is an autonomous AI agent that strategically engages with Twitter conversations to boost brand visibility. The agent:

1. **Monitors Discussions**  
   - Tracks replies to specified project tweets
   - Identifies relevant conversations using keywords/themes
   - Filters out already-answered comments

2. **Generates Context-Aware Responses**  
   - Uses OpenAI to craft natural-sounding replies
   - Maintains brand voice (positive, constructive, human-like)
   - Strictly follows Twitter character limits

3. **Manages Engagement**  
   - Enforces delays between posts to avoid spam
   - Tracks answered comments in Redis
   - Handles rate limits and API errors gracefully

## Prerequisites

### System Requirements
- Python 3.10+
- Redis 6.2+ (for conversation tracking)
- Ray Serve (for deployment)

### API Keys
- **Twitter API**:
  - Obtain through Twitter Developer Portal
  - Requires OAuth 2.0 with tweet/write permissions

- **OpenAI API**:
  - GPT-4/GPT-3.5 access required
  - Key with at least 100K tokens/month recommended

### Environment Variables
```bash
# Required
export TWITTER_ACCESS_TOKEN="your_twitter_bearer_token"
export OPENAI_API_KEY="sk-your-openai-key"
export REDIS_URL="redis://default:password@localhost:6379"

# Optional (defaults)
export POST_DELAY_SECONDS="60"  # Minimum between replies
export MAX_COMMENT_LENGTH="280" # Twitter character limit
```

## Quickstart

### Local Deployment
```bash
# 1. Install dependencies
poetry install

# 2. Set environment variables
cp .env.example .env
nano .env  # Add your credentials

# 3. Run with Ray Serve
serve run twitter_ambassador_comments_answerer:app
```

### Usage Example
```python
import requests

response = requests.post(
    "http://localhost:8000/nfinify_ai.nfinity_io.web3,ai.decentralization",
    json={
        "plan": {"max_comments": 5}  # Optional parameters
    }
)
```