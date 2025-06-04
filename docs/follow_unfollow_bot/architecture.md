# Architecture & Flow

## Overview
FollowUnfollowBot combines scheduled tasks with API control for Twitter growth automation:

1. **Background Processing**:
   - Continuous follow-for-like strategy
   - Daily follow limit resets

2. **Database Layer**:
   - SQLAlchemy-managed PostgreSQL
   - User tracking
   - Daily limits enforcement

3. **API Control**:
   - Add/remove users
   - Manual overrides

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- FastAPI HTTP interface
- Background task workers
- PostgreSQL data storage
- Twitter API integration

## Task Scheduling
| Task | Frequency | Description |
|------|-----------|-------------|
| `background_task` | Hourly | Executes follow-for-like strategy |
| `daily_task` | Midnight | Resets daily follow counters |
