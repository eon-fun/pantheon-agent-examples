# API & Configuration Reference

## REST Endpoints

### `POST /add_account`
Adds Twitter account to monitoring list

#### Request Body
```json
{"account": "twitterhandle"}
```

#### Responses
- Success: `{"status": "success"}`
- Error: `{"status": "error", "message": "..."}`

## Configuration

### Environment Variables
| Variable | Description |
|----------|-------------|
| `TWITTER_BEARER_TOKEN` | Twitter API v2 bearer token |
| `OPENAI_API_KEY` | OpenAI API key |
| `TELEGRAM_*` | Telegram integration keys |
| `REDIS_URL` | Redis server URL |

### Monitoring Parameters
| Parameter | Value |
|-----------|-------|
| Scan Interval | 6 hours |
| Max Tweets | All new since last scan |
| Summary Style | Concise, bullet-pointed |
