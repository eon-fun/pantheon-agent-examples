# Architecture & Flow

## Overview
KolAgent coordinates Twitter engagement campaigns through:
1. Redis-stored account management
2. Twitter API authentication workflow
3. Background task execution
4. Langfuse observability integration

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- Client interaction via FastAPI
- Redis for account credential storage
- Twitter API for engagement actions
- Langfuse for execution tracing

## Flow Description
1. **Raid Initialization**:
   - Client POSTs target tweet and bot accounts
   - Agent validates inputs and starts background task
   - Langfuse trace begins

2. **Account Processing**:
   - Retrieves account credentials from Redis
   - Obtains fresh Twitter access tokens
   - Distributes engagement actions

3. **Monitoring**:
   - All actions logged to Langfuse
   - Errors captured and reported
   - Duration controlled by raid_minutes

4. **Account Management**:
   - GET /all_accounts verifies all stored accounts
   - Returns current authentication status
   - Identifies problematic accounts
