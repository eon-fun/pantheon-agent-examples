# Architecture & Flow

## Overview
NewsAggregatorBot implements a content pipeline with:

1. **Collection Layer**:
   - Website scraping (BeautifulSoup)
   - Twitter API integration
   - Grok AI search

2. **Processing Layer**:
   - HTML content extraction
   - AI-powered rewriting
   - Markdown formatting

3. **Delivery Layer**:
   - Rate-limited Telegram publishing
   - Message queue management
   - Error handling

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- Telegram interaction points
- Content sources
- Processing components
- Data storage

## Content Flow
1. Periodic source checks (10s interval)
2. New content detection
3. AI processing (OpenAI/Grok)
4. Queue management
5. Scheduled publishing
