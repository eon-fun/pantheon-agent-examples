# Twitter Commentator Agent

## Overview
The Twitter Commentator Agent is an automated system that monitors specified Twitter accounts and generates contextually relevant comments on their tweets. Built with FastAPI and Ray Serve, this agent handles the entire workflow from fetching new tweets to posting appropriate comments while respecting rate limits.

## Features
- Automatically detects and comments on new tweets from target accounts
- Avoids duplicate comments by tracking interaction history
- Implements rate limiting to comply with Twitter API restrictions
- Persists data using Redis for reliable operation

## Architecture
The agent is built using:
- **FastAPI**: For API endpoints and request handling
- **Ray Serve**: For deployment and scaling
- **Redis**: For persistent storage and rate limit management
- **Twitter API**: For tweet fetching and comment posting

## Usage
To use the agent, send a POST request to the `/{goal}` endpoint where `goal` is formatted as:

```
{commenting_username}.{target_username}
```

- `commenting_username`: Your Twitter account that will be posting comments
- `target_username`: The Twitter account whose tweets you want to comment on

## Workflow
1. Fetches recent tweets from the target user
2. Filters out tweets that have already been commented on
3. Generates a contextually relevant comment for the newest tweet
4. Posts the comment to Twitter after ensuring appropriate delay
5. Records the interaction in Redis for future reference


## Configuration
The agent uses several utility modules which should be configured separately:
- Twitter API credentials should be managed through the `TwitterAuthClient`
- Rate limiting parameters can be adjusted in the Redis client implementation
- Comment generation strategies can be customized in the commentator module
