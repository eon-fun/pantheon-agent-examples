# TwitterLikerAgent

## Purpose & Scope

TwitterLikerAgent is a Ray Serve-based microservice that searches for tweets based on given keywords and themes, then likes a random selection of them using the user's Twitter account.

## Prerequisites

- Python 3.10+
- Ray Serve runtime
- Redis database
- Twitter developer credentials (handled via `TwitterAuthClient`)
- Dependencies from internal Pantheon CodeArtifact repository

### Required Environment Variables

- `TWITTER_CLIENT_ID`, `TWITTER_CLIENT_SECRET` — Twitter API credentials
- Redis host credentials (implicitly used by `get_redis_db`)
- Internal packages must be resolvable via Poetry and configured source

## Quickstart

1. **Install dependencies:**

   ```bash
   poetry install
2. **Run the agent locally using Ray Serve:**
    
    ```bash
   poetry run python twitter_ambassador_liker/entrypoint.py
   ```
3. **Send a test request:**

    ```bash
   curl -X POST http://localhost:8000/myusername.keyword1-keyword2.theme1-theme2
   ```

**The agent will:**

 - Retrieve access token for myusername

 - Search for tweets using keyword1, keyword2, theme1, theme2

 - Like up to 3 unseen tweets

 - Store liked tweet IDs in Redis to prevent duplication

