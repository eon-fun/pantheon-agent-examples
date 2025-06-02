# Twitter Auto Liker Agent (Ray Serve Implementation)

A scalable Twitter engagement agent built on Ray Serve that automatically likes relevant tweets based on predefined keywords and themes.

## Features

- **Ray Serve Integration**: Deployed as a scalable microservice with FastAPI
- **Custom Goal Format**: Parses username, keywords, and themes from a simple string format
- **Targeted Tweet Discovery**: Searches for high-quality content matching your interests
- **Engagement Tracking**: Redis-backed system prevents duplicate interactions
- **Natural Behavior Patterns**: Random delays and selection amounts mimic human activity

## Usages

### Start the Ray Serve Service

### Send Requests

The agent accepts POST requests with a goal parameter in the format:
`username.keyword1,keyword2.theme1,theme2`

```bash
# Example request
curl -X POST "http://localhost:8000/twitter_user.[AIWeb3,crypto].[NFT,blockchain]"
```

## Goal Format

The goal string follows this format:
- Part 1: Twitter username
- Part 2: Comma-separated keywords (no spaces)
- Part 3: Comma-separated hashtag themes (no spaces)

Example: `crypto_enthusiast.[AIWeb3,decentralized].[NFT,blockchain,Web3]`
