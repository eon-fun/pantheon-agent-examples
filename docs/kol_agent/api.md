# API & Configuration Reference

## REST Endpoints

### `POST /{goal}`
Initiates a Twitter engagement campaign.

#### Request Body
```json
{
  "target_tweet_id": "1719810222222222222",
  "tweet_text": "Engagement content",
  "bot_accounts": [
    {
      "username": "account1",
      "role": "advocate",
      "account_access_token": "token123",
      "user_id": "12345"
    }
  ],
  "raid_minutes": 0.1
}
```

#### Responses
**Success (200):**
```json
{
  "success": true,
  "message": "Raid started"
}
```

### `GET /all_accounts`
Lists all configured bot accounts with status.

#### Responses
**Success (200):**
```json
{
  "accounts": [
    {
      "account": "bot1",
      "user_id": "12345",
      "access_token": "token123"
    }
  ],
  "excepted_errors": []
}
```

## Configuration Reference

### Environment Variables
| Variable | Description |
|----------|-------------|
| `REDIS_URL` | Redis connection URL |
| `TWITTER_CLIENT_ID` | Twitter OAuth2 client ID |
| `TWITTER_CLIENT_SECRET` | Twitter OAuth2 client secret |
| `LANGFUSE_*` | Langfuse observability keys |

### Redis Data Structure
- Accounts stored as Redis keys
- Each account requires:
  - Twitter username
  - OAuth2 refresh token
  - Metadata (user_id, etc.)
