# Architecture & Flow

## Overview
TweetProcessor implements a content pipeline with:

1. **Collection Layer**:
   - Twitter API v2 integration
   - Account-based monitoring
   - Rate-limited requests
   - Error handling

2. **Processing Layer**:
   - AI-powered summarization
   - Content sanitization
   - HTML formatting
   - Duplicate detection

3. **Delivery Layer**:
   - Telegram channel integration
   - Formatted message output
   - Error-resilient publishing

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- Ray distributed processing
- Twitter API integration
- OpenAI processing
- Redis state management

## Content Flow
1. Periodic account checks (30s interval)
2. New tweet detection
3. AI summarization
4. Telegram publishing
5. State updates
