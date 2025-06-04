# Architecture & Flow

## Overview

The `TwitterAmbassadorCommentsAnswerer` is a Ray Serve-based agent that automatically engages with tweet replies on behalf of a specified Twitter account. It uses a goal string to identify target conversations, generates AI-powered responses, and maintains reply history in Redis.

## Component Diagram

See [`architecture.puml`](./architecture.puml) for the component layout, including:
- FastAPI + Ray Serve deployment
- External dependencies: Twitter API, OpenAI API, and Redis
- Internal utilities: `twitter_ambassador_utils`, `tweetscout_utils`, and `redis_client`

## Flow Description

1. **User sends POST /{goal} request** to the agent (format: `username.project.keywords.themes`)
2. The agent:
   - Parses the goal into components
   - Authenticates with Twitter using `TwitterAuthClient`
   - Searches for relevant replies using `search_tweets()`
   - Filters out already-answered comments via Redis
   - Uses OpenAI to check if response is needed (`check_answer_is_needed()`)
   - Generates human-like replies (`create_comment_to_comment()`)
   - Posts responses with enforced delays (`ensure_delay_between_posts`)
   - Records answered tweet IDs in Redis

## Key Features
- **Natural Engagement**: AI-generated replies mimic human conversation patterns
- **Duplicate Prevention**: Redis tracks all answered comments
- **Rate Control**: Minimum 60-second delay between replies
- **Safety Checks**: Validates replies for appropriate content before posting