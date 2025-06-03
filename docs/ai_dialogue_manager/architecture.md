# Architecture & Flow

## Overview

The `TelegramSummarizer` is a Telethon-based agent that collects and summarizes unread messages, mentions, and replies across Telegram chats. It stores message context in Redis and generates AI-powered digests via OpenAI's API when triggered by the `/summary` command.

## Component Diagram

See [`architecture.puml`](./architecture.puml) for the high-level flow including:
- Telegram client connection via Telethon
- Redis storage for message persistence
- OpenAI API integration for summarization
- Three key internal handlers: message collector, cleaner, and summarizer

## Flow Description

1. **Message Collection Trigger**:
   - The agent monitors all incoming Telegram messages
   - For each message, it checks:
     ```python
     if (not message.out) and (message.unread or 
         message.mentioned or message.is_reply)
     ```
   - Valid messages are stored in Redis as timestamped JSON objects

2. **Summary Generation**:
   - When user sends `/summary` command:
     - Agent first purges read messages via `clean_read_messages()`
     - Combines remaining messages with metadata:
       ```text
       [Chat Name] @username action: message text
       ```
     - Sends structured prompt to OpenAI with strict summarization rules
     - Returns formatted digest grouped by chat

3. **Data Management**:
   - Redis sorted set ensures chronological ordering
   - Automatic cleanup after summary generation
   - Failed API calls trigger graceful degradation:
     - Redis failures → in-memory fallback
     - OpenAI errors → simplified local summary

## Key Components

| Component | Responsibility |
|-----------|----------------|
| `collect_messages` | Filters and stores relevant messages |
| `clean_read_messages` | Maintains storage hygiene |
| `generate_summary` | Orchestrates AI summarization |
| Redis Client | Persistent message storage |
| Telethon Client | Real-time Telegram interaction |

## Behavioral Notes
- Introduces 2-5 second delays during processing to avoid rate limits
- Strictly avoids message content modification
- Preserves original sender attribution in summaries