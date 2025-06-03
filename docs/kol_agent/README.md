# KolAgent

## Purpose & Scope
KolAgent orchestrates coordinated Twitter engagement campaigns ("raids") using multiple bot accounts to amplify messages. It manages authentication, timing, and content distribution across accounts.

## Prerequisites
- Python 3.10+
- Redis instance for account storage
- Twitter API credentials for all bot accounts
- Langfuse account for observability
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `REDIS_URL` - Redis connection string
- `TWITTER_CLIENT_ID` - Twitter OAuth2 client ID
- `TWITTER_CLIENT_SECRET` - Twitter OAuth2 client secret
- `LANGFUSE_PUBLIC_KEY` - Langfuse observability key
- `LANGFUSE_SECRET_KEY` - Langfuse secret key
- `LANGFUSE_HOST` - Langfuse server URL

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export REDIS_URL="redis://localhost:6379"
   export TWITTER_CLIENT_ID="your-twitter-client-id"
   export TWITTER_CLIENT_SECRET="your-twitter-client-secret"
   export LANGFUSE_PUBLIC_KEY="your-langfuse-key"
   export LANGFUSE_SECRET_KEY="your-langfuse-secret"
   export LANGFUSE_HOST="https://cloud.langfuse.com"
   ```

3. **Run the agent:**
   ```bash
   serve run kol_agent:app
   ```

4. **Start a raid:**
   ```bash
   curl -X POST "http://localhost:8000/amplify" \
   -H "Content-Type: application/json" \
   -d '{
     "target_tweet_id": "1719810222222222222",
     "tweet_text": "Our revolutionary new product!",
     "bot_accounts": [
       {
         "username": "example_bot1",
         "role": "advocate",
         "account_access_token": "token1",
         "user_id": "12345"
       }
     ],
     "raid_minutes": 0.1
   }'
   ```
