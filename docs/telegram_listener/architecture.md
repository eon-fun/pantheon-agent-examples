# Architecture & Flow

## Overview
TelegramListenerAgent is a Ray Serve deployment that monitors Telegram channels using Telethon library. It provides real-time message processing with automatic reconnection capabilities through a FastAPI control interface.

## Component Diagram
See [`architecture.puml`](./architecture.puml) for visual representation of:

- Telegram MTProto server connection
- FastAPI control plane
- Telethon client management
- Message processing pipeline
- Automatic reconnection handler

## Flow Description

### Startup Sequence
1. **Initialization**:
   - FastAPI app starts with lifespan manager
   - Data processing backend initializes
   - Telethon client manager prepares session

2. **Connection Establishment**:
   - Client connects to Telegram MTProto servers
   - User authorization verified (may require 2FA)
   - Event handler registered for target chat

### Message Processing Flow
1. **Event Reception**:
   - NewMessage event triggers handler
   - Message metadata validated
   - Chat ID filtered against target

2. **Data Processing**:
   ```plaintext
   Raw Message → Parser → Validator → Transformer → Output
   ```
   - Content extraction
   - Media handling (if present)
   - Metadata enrichment

3. **Downstream Delivery**:
   - Processed messages queued
   - Error isolation per message
   - Retry logic for transient failures

### Connection Management
- **Automatic Reconnect**:
  - 5-second heartbeat check
  - Exponential backoff (15s → 60s)
  - Handler re-registration

- **Error Handling**:
  - Flood wait detection (auto-pause)
  - Permission error escalation
  - Auth failures (session invalidation)
