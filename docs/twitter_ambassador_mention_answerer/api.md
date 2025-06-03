# API & Configuration Reference

## Public API Endpoint

### `POST /{goal}`
Starts monitoring mentions for specified account.

#### Request Format
```bash
username.keywords.hashtags
```

#### Parameters
| Component  | Description                          | Example             |
|------------|--------------------------------------|---------------------|
| `username` | Twitter handle to monitor            | `cryptodev`         |
| `keywords` | Comma-separated terms to track       | `defi,web3,staking` |
| `hashtags` | Comma-separated relevant hashtags    | `crypto,blockchain` |

#### Response
```json
{
  "status": "monitoring_started",
  "account": "username",
  "first_check_completed": true,
  "mentions_found": 3
}
```

## Configuration Options

### Environment Variables
```bash
# Required
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
export OPENAI_API_KEY="your_openai_key"

# Optional (with defaults)
export POLL_INTERVAL=300       # Check every 5 minutes
export MIN_REPLY_DELAY=120     # 2 minutes between replies
export MAX_HISTORY_DAYS=7      # Keep 7 days of history
```

### Rate Limits
- **API Checks**: 15 requests/hour
- **Replies**: 1 per 2 minutes per account
- **History**: Last 50 mentions stored

## Example Request
```bash
curl -X POST http://localhost:8000/cryptodev.defi,web3.crypto,blockchain
```

## Example Response
```json
{
  "status": "monitoring_started",
  "account": "cryptodev",
  "first_check_completed": true,
  "mentions_found": 2,
  "last_checked": "2023-11-15T14:30:00Z"
}
```
