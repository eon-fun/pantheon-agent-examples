# Architecture & Flow

## Overview
TwitterPostingAgent uses a decision tree to determine optimal content type based on:
- User's posting history (from Redis)
- Recent project tweets (from Twitter API)
- Content generation rules (via OpenAI)

## Component Diagram
See [`architecture.puml`](./architecture.puml) for a high-level sequence diagram, including:

Key components:
1. **Request Handler** - Processes incoming POST requests
2. **Content Router** - Decides tweet type based on history
3. **Prompt Engine** - Formats OpenAI prompts for each content type
4. **Post Manager** - Handles Twitter API interactions

## Flow Logic
1. **New Accounts**:
   - Generates introductory tweet using base prompt
   - Stores first post in Redis

2. **Regular Posting Cycle**:
   - Checks last post type (news/regular/quote)
   - Maintains 1:2:1 ratio between news:regular:quote
   - Ensures no content type repetition

3. **Content Validation**:
   - Formats text with proper paragraph breaks
   - Ensures 260-character limit
   - Removes prohibited elements (hashtags/emojis)