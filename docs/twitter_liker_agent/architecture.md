# Architecture & Flow

## Overview

The `TwitterLikerAgent` is a Ray Serve-based agent that automatically likes tweets on behalf of a specified Twitter user. It uses a goal string to derive keywords and themes, searches for relevant tweets, filters out already liked ones using Redis, and then performs like actions via the Twitter API.

## Component Diagram

See [`architecture.mmd`](./architecture.mmd) for a high-level component layout, including:
- The FastAPI + Ray Serve deployment
- External service dependencies: Twitter API and Redis
- Internal utility packages: `twitter_ambassador_utils`, `tweetscout_utils`, and `redis_client`

## Flow Description

1. **User sends POST /{goal} request** to the agent.
2. The agent:
   - Parses the `goal` string into `username`, `keywords`, and `themes`
   - Authenticates with Twitter using `TwitterAuthClient`
   - Retrieves the set of previously liked tweets from Redis
   - Performs searches via `search_tweets()` for both keywords and themes
   - Filters out already liked tweets
   - Likes 1 to 3 new tweets using the Twitter API (`set_like`)
   - Records liked tweet IDs back into Redis

This process ensures that no tweet is liked more than once, and introduces randomized timing to simulate human-like behavior.
