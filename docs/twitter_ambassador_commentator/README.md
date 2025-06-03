# TwitterCommentatorAgent

## Purpose & Scope

TwitterCommentatorAgent is a Ray Serve microservice that automatically comments on tweets from a specified Twitter user. It acts as an AI-powered Twitter ambassador, creating positive, natural, and concise comments to engage the community and promote projects.

## Prerequisites

- Python 3.10+
- Ray Serve runtime
- Redis database
- Twitter developer credentials (managed via `TwitterAuthClient`)
- Dependencies installed via Poetry from the internal Pantheon CodeArtifact repository

### Required Environment Variables

- `TWITTER_CLIENT_ID`, `TWITTER_CLIENT_SECRET` — Twitter API credentials
- Redis host credentials (used implicitly by `get_redis_db`)
- Poetry configured to resolve internal Pantheon package sources

## Quickstart

1. **Install dependencies:**

   ```bash
   poetry install
   ````

2. **Run the agent locally with Ray Serve:**

   ```bash
   poetry run python twitter_ambassador_commentator/entrypoint.py
   ```

3. **Send a POST request to trigger commenting:**

   ```bash
   curl -X POST http://localhost:8000/myusername.projectusername
   ```

**Agent workflow:**

* Retrieves the Twitter access token for `myusername`.
* Fetches recent tweets from `projectusername`.
* Generates AI-based positive comments for tweets that were not commented on previously.
* Posts comments to Twitter using the authenticated account.
* Stores commented tweet IDs in Redis to avoid duplicates.
* Ensures delays between posts to respect rate limits.

## Development

* Tests are run via pytest.
* Use Poetry to manage dependencies and packaging.
* Ray Serve is used to deploy the agent with HTTP ingress.

