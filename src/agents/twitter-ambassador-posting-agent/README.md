# Twitter Posting Agent

## Overview
The Twitter Posting Agent is an automated system that creates and publishes diverse types of tweets for ambassador accounts. It intelligently cycles between regular tweets, news summaries, and quote tweets to maintain an authentic and engaging social media presence while promoting specified keywords and themes.

## Features
- Creates diverse tweet content based on user history and context
- Implements a smart content rotation strategy with three tweet types:
  - Regular tweets about project topics
  - News summary tweets highlighting relevant industry developments
  - Quote tweets that engage with existing project content
- Leverages AI-generated content with project knowledge integration
- Tracks posting history to guide future content decisions
- Manages rate limiting to comply with Twitter API restrictions

## Architecture
The agent is built using:
- **FastAPI**: For API endpoints and request handling
- **Ray Serve**: For deployment and scaling
- **Redis**: For persistent storage and tweet history tracking
- **Twitter API**: For posting tweets and fetching timeline data
- **OpenAI**: For AI-powered content generation

## Usage
To use the agent, send a POST request to the `/{goal}` endpoint where the goal parameter contains:

```
{your_username}.{[keywords]}.{[themes]}
```

## Workflow
1. Analyzes the user's tweet history to determine what type of content to create next
2. Follows a content strategy that alternates between:
   - Regular tweets about specified topics
   - News summary tweets that highlight relevant recent developments (for tweets not preceded by a news summary)
   - Quote tweets that engage with other relevant content (if no quote tweets in last two posts)
3. Generates appropriate tweet content using OpenAI with project-specific knowledge prompts
4. Posts the content to Twitter after ensuring appropriate delay
5. Records the new post in Redis for future reference

## Content Generation Logic
The agent uses several helper functions for content creation:
- `_create_tweet`: Generates regular tweets about project topics
- `_create_news_tweet`: Creates news summary tweets based on recent high-engagement content
- `_create_quoted_tweet`: Crafts appropriate comments for quote tweets

Each function leverages project knowledge prompts to ensure content is relevant and on-brand.

## Tweet Selection Logic
- If the user has no previous tweets, creates a first regular tweet
- If the last tweet was not a news summary, creates a news summary tweet
- If the last two tweets did not include quote tweets, searches for project content to quote
- Otherwise, creates a regular tweet with fresh content

## News Tweet Generation
The agent searches for recent news tweets (last 24 hours) related to specified keywords and themes with at least 100 likes, prioritizing longer content (>200 characters) for substantial news summaries.
