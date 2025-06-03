# API & Configuration Reference

## REST Endpoints

### `POST /{twitter_id}.{action}`
Manages user tracking in the system.

#### Path Parameters
- `twitter_id`: Twitter user ID (e.g., `12345`)
- `action`: Either `add` or `delete`

#### Responses
**Success (200):**
```json
{
  "status": "success",
  "action": "added",
  "user_id": 12345
}
```

## Configuration Reference

### Environment Variables
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection URL |
| `TWITTER_API_*` | Twitter API credentials |
| `DAILY_FOLLOW_LIMIT` | Max follows/day (default: 400) |

### Database Schema
Key tables:
- `users`: Tracked accounts
- `follow_limits`: Daily counters
- `follow_history`: Audit log
