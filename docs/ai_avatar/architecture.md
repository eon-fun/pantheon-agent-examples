# Architecture & Flow

## Overview
AI Avatar is a Telegram bot that:
1. Analyzes user's communication style (last 100 messages)
2. Generates personalized responses using OpenAI API
3. Maintains conversation context in Redis

## Component Diagram
See [`architecture.puml`](./architecture.puml) for a high-level sequence diagram, including:

## Flow Description

1. **User sends `/new_style`** via Telegram.
2. The bot:
   - Fetch recent user messages (<=100).
   - Store/fetch user context (user:<user_id>).
   - Prepare prompt with user style.
   - Store response in Redis.
   - Send response via Telegram.

## Data Flow
1. **User Interaction**:
   - Sends regular message or `/new_style` command
   - Receives stylistically-matched responses

2. **Key Features:**

- Style adaptation using message history

- Context preservation between sessions

- Manual style refresh via /new_style

##Error Handling
- Redis failures: Continue without cached context

- OpenAI errors: Return user-friendly message

- Telegram API issues: Retry with exponential backoff