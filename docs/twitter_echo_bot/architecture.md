# Architecture & Flow

## Overview
FollowUnfollowBot combines scheduled tasks with API control for Twitter automation:

1. **Core Services**:
   - `TwitterCollectorClient`: Fetches tweets from tracked accounts
   - `CreateTweetsService`: Generates persona-based content
   - User management handlers

2. **Data Layer**:
   - SQLAlchemy-managed PostgreSQL
   - User profiles storage
   - Tracked accounts relationships

3. **Operation Modes**:
   - Background tasks (automatic)
   - API endpoints (manual control)

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- FastAPI HTTP interface
- Background workers
- Twitter API integration
- Database schema

## Task Scheduling
| Task | Interval | Description |
|------|----------|-------------|
| Tweet Collection | 500s | Fetches new tweets |
| Content Generation | 5s | Creates persona-based posts |
