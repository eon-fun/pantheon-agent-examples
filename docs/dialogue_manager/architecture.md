# Architecture & Flow

## Overview
DialogueManager implements a conversation processing pipeline with:

1. **Collection Layer**:
   - Telegram message monitoring (Telethon)
   - Command processing (/summary)
   - Message metadata extraction

2. **Storage Layer**:
   - Redis-backed message storage
   - Sorted sets for chronological ordering
   - Read state tracking

3. **Processing Layer**:
   - AI-powered summarization
   - Context-aware processing
   - Error handling

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- FastAPI interface
- Telethon integration
- Redis data management
- OpenAI processing

## Message Flow
1. Telegram message received
2. Metadata extraction
3. Redis storage
4. AI processing on demand
5. Summary delivery
