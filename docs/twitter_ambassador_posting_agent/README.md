# TwitterPostingAgent

## Purpose & Scope
TwitterPostingAgent is an autonomous AI Twitter ambassador that:
- Generates and posts organic tweets for specified accounts
- Maintains natural posting rhythm with varied content types
- Ensures brand-aligned messaging using predefined prompts

## Prerequisites
- Python 3.10+
- FastAPI and Ray Serve for API endpoints
- Twitter API v2 credentials
- Redis for post history storage
- OpenAI API for content generation

### Required Environment Variables
- `TWITTER_API_KEY` - Twitter developer API key
- `TWITTER_API_SECRET` - Twitter developer API secret
- `OPENAI_API_KEY` - OpenAI API key for text generation
- `REDIS_URL` - Redis connection string (optional)

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   export TWITTER_API_KEY="your_twitter_key"
   export TWITTER_API_SECRET="your_twitter_secret" 
   export OPENAI_API_KEY="your_openai_key"
   ```

3. **Run the agent:**
   ```bash
   python -m twitter_posting_agent.main
   ```

4. **Trigger tweet generation:**
   ```bash
   curl -X POST http://localhost:8000/johndoe.defi,web3.crypto,blockchain
   ```
   Where:
   - `johndoe` = Twitter handle
   - `defi,web3` = content keywords
   - `crypto,blockchain` = theme hashtags