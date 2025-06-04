# API Reference

## Core Endpoint

### `POST /{goal}`
Main endpoint for triggering comment engagement workflow.

#### Goal Parameter Structure
```
{your_bot_username}.{target_project}.{keywords}.{themes}
```
Example:  
`nfinify_ai.nfinity_io.web3,defi.decentralization,ai`

#### Request Body (Optional)
```json
{
  "plan": {}
}
```

#### Response Codes
| Code | Description |
|------|-------------|
| 200  | Successfully processed comments |
| 400  | Invalid goal format |
| 401  | Twitter/OpenAI auth failed |
| 429  | Twitter API rate limit hit |
| 500  | Internal processing error |

## Response Format

### Success (200)
```json
{
  "status": "completed",
  "metrics": {
    "scanned_comments": 42,
    "responded_to": 3,
    "skipped_already_answered": 39,
    "time_elapsed": "12.7s"
  },
  "new_comments": [
    {
      "tweet_id": "1786604234150453248",
      "response_text": "Great point about decentralization...",
      "response_url": "https://twitter.com/i/web/status/1786604234150453248"
    }
  ]
}
```

### Error (4xx/5xx)
```json
{
  "error": "TWITTER_AUTH_FAILURE",
  "detail": "Invalid access token",
  "recovery": "Refresh OAuth2 token via Twitter Developer Portal"
}
```

## Underlying API Interactions

### Twitter API Calls
| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET`  | `/2/tweets/search/recent` | Find relevant replies |
| `POST` | `/2/tweets` | Post comment replies |


## Error Handling
The agent provides clear error states:

| Error Case | Response | Resolution |
|------------|----------|------------|
| Invalid goal format | 422 Unprocessable Entity | Use `user.project.keywords.themes` |
| Twitter API limit | 429 Too Many Requests | Wait 15 minutes |
| OpenAI failure | 502 Bad Gateway | Check API key validity |
| Redis unavailble | 503 Service Unavailable | Verify Redis connection |


## Rate Limits
- **Twitter**: 50 requests/15 minutes (per token)
- **OpenAI**: 3,500 RPM / 90,000 TPM
- **Redis**: 10,000 writes/second

