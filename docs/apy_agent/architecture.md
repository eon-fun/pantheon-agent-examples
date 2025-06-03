# Architecture & Flow

## Overview
APYAgent combines Telegram bot interface with DeFi analytics:

1. **User Interaction**:
   - Telegram command parsing
   - Status updates
   - Markdown-formatted results

2. **Data Processing**:
   - Multi-protocol analysis
   - Token price validation
   - APY-based ranking

3. **Safety Checks**:
   - APY validation
   - Token activity
   - Data completeness
   - Timeliness checks

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- Telegram user flow
- Enso API integration
- Data validation process
- Recommendation generation

## Analysis Process
1. Protocol discovery
2. Token scanning
3. Pool validation
4. Top-5 ranking
5. Recommendation formatting

