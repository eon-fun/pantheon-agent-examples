# Twitter Comment Responder Agent

A Ray Serve application that automatically monitors and responds to comments on Twitter posts for specified project accounts.

## Overview

This agent scans for comments directed at a target Twitter account that match defined keywords and themes, then generates and posts contextually relevant responses.

## Features

- **Targeted Monitoring**: Tracks comments directed at specific project accounts
- **Contextual Response Generation**: Creates appropriate replies based on conversation context
- **Keyword & Theme Filtering**: Focuses on relevant discussions using configurable parameters
- **Duplication Prevention**: Tracks previously responded comments to avoid duplicates
- **Rate Limiting**: Ensures posts maintain natural timing with configurable delays
- **Conversation Awareness**: Analyzes full conversation threads for more meaningful responses

## Usages

The agent accepts POST requests with a goal parameter in the format:
`your_username.project_username.keyword1,keyword2.theme1,theme2`

```bash
# Example request
curl -X POST "http://localhost:8000/social_agent.company_account.[AI,blockchain,crypto].[Web3,NFT,DeFi]"
```

### Goal Format

The goal string follows this pattern:
1. Your Twitter username
2. Project username to monitor
3. Comma-separated keywords (no spaces)
4. Comma-separated hashtag themes (no spaces)

## Requirements

- Ray Serve
- FastAPI
- Redis client
- Twitter API authentication utilities
- TweetScout utilities for conversation analysis

## Configuration

Set up your environment variables:

```bash
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
export REDIS_URL="your_redis_connection_string"
```
