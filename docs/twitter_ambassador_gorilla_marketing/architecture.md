# Architecture Overview

## Component Diagram

See [`architecture.puml`](./architecture.puml) for a high-level sequence diagram, including:

### Key Components
1. **Main Agent** 
   - Orchestrates the entire workflow
   - Handles API requests and response formatting
   - Manages rate limiting through Redis

2. **Twitter API Client**
   - Handles authentication (OAuth 2.0)
   - Executes tweet searches (`/2/tweets/search/recent`)
   - Posts replies (`/2/tweets`)

3. **AI Gateway**
   - Validates tweet relevance using `PROMPT_FOR_CHECK`
   - Generates organic comments via `PROMPT_FOR_COMMENT`

4. **Redis Store**
   - Tracks commented tweets (`gorilla_marketing_answered:{username}`)
   - Enforces posting delays (5+ minutes between comments)
   - Stores post history (`user_posts:{username}`)

## Safety Mechanisms
1. **AI Pre-Screening** - All tweets pass through:
   - Relevance check (technical content only)
   - Brand safety filter (no price discussions)
   - Organic tone verification

2. **Rate Limiting**
   - 5+ minute delay between comments
   - Max 2 comments per execution
   - Redis-tracked post history

3. **Blacklisting**
   - Automatic skip of previously answered tweets
   - Exclusion of own account tweets
