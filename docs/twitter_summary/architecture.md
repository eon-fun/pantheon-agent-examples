# Architecture & Flow

## Overview
TweetProcessor implements a content pipeline with:

1. **Data Collection**:
   - Twitter API v2 integration
   - Account-based tweet fetching
   - Redis-backed duplicate prevention

2. **Processing**:
   - OpenAI-powered summarization
   - HTML content sanitization
   - Batch processing

3. **Delivery**:
   - Telegram channel integration
   - Formatted message output
   - Error-resilient delivery

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- API management interface
- Background processing flow
- External service integrations
- Data persistence layer

## Content Flow
1. Account discovery (Redis)
2. Tweet collection (Twitter API)
3. Deduplication (Redis)
4. Summarization (OpenAI)
5. Delivery (Telegram)
