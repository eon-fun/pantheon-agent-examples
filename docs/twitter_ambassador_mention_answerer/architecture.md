# Architecture & Flow

## Overview
TwitterMentionsMonitor implements a real-time mention response system with:
- Continuous polling of Twitter mentions API
- Conversation context analysis
- Intelligent reply generation
- Anti-spam timing controls

## Component Diagram
See [`architecture.puml`](./architecture.puml) for a high-level sequence diagram, including:

Key components:
1. **Mention Fetcher** - Polls Twitter API for new @mentions
2. **Context Builder** - Retrieves full conversation threads
3. **Reply Generator** - Creates context-aware responses using OpenAI
4. **Rate Limiter** - Enforces minimum 2-minute delay between replies

## Flow Logic
1. **Mention Detection**:
   - Checks for new @mentions every 5 minutes
   - Filters out retweets and already-responded mentions
   - Validates mention requires response

2. **Context Analysis**:
   - Fetches entire conversation thread
   - Identifies keywords and conversation topic
   - Determines appropriate response tone

3. **Reply Posting**:
   - Generates human-like response
   - Enforces timing delays between replies
   - Records responded mentions in Redis