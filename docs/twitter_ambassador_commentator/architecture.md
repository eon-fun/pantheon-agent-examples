# Architecture & Flow

## Overview

The `TwitterAmbassadorCommentator` is a Ray Serve-based agent that automatically posts comments on tweets from specified project accounts on behalf of a user. It processes a goal string containing the commentator's and project's Twitter usernames, fetches recent tweets from the project, avoids commenting multiple times on the same tweet using Redis tracking, and uses OpenAI to generate natural comments before posting replies.

## Component Diagram

See [`architecture.puml`](./architecture.puml) for a high-level component layout, including:
- The FastAPI + Ray Serve deployment
- External service dependencies: Twitter API, Redis, and OpenAI API
- Internal utility packages: `twitter_ambassador_utils`, `tweetscout_utils`, and `redis_client`

## Flow Description

1. **User sends POST /{goal} request** to the agent.
2. The agent:
   - Parses the `goal` string into `my_username` and `project_username`
   - Authenticates with Twitter via `TwitterAuthClient` for `my_username`
   - Retrieves tweets from `project_username` using `fetch_user_tweets()`
   - Checks Redis for tweets already commented on
   - Generates a positive comment using OpenAI for the first uncommented tweet
   - Posts the comment as a reply to the tweet via Twitter API
   - Stores the commented tweet ID in Redis to prevent duplicates
   - Applies rate limiting/delays using Redis to simulate human behavior

This ensures targeted, human-like engagement while avoiding spam and duplicate comments.
