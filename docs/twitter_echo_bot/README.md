# TwitterEchoBot

## Purpose & Scope
FollowUnfollowBot manages Twitter account tracking and content generation by:
- Collecting tweets from tracked accounts
- Generating persona-based content
- Managing user profiles and preferences
- Automating engagement activities

## Prerequisites
- Python 3.10+
- PostgreSQL database
- Twitter API credentials
- Redis (optional for caching)
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `TWITTER_API_KEY` - Twitter API key
- `TWITTER_API_SECRET` - Twitter API secret
- `TWITTER_ACCESS_TOKEN` - Twitter access token
- `TWITTER_ACCESS_SECRET` - Twitter access token secret

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize database:**
   ```bash
   python -c "from DB.sqlalchemy_database_manager import init_models; asyncio.run(init_models())"
   ```

3. **Run the agent:**
   ```bash
   serve run follow_unfollow_bot:app
   ```

4. **Manage users:**
   ```bash
   # Add new user
   curl -X POST "http://localhost:8000/12345.add_user.johndoe"

   # Update user preferences
   curl -X POST "http://localhost:8000/12345.update_user.johndoe.professional.tech_enthusiast"
   ```

**Key Features:**
- Background tweet collection
- Automated content generation
- User profile management
- Account tracking system
