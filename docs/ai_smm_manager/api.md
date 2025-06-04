# API & Configuration Reference

## Telegram Commands

### `/add_links <url1> <url2>...`
Adds news websites to monitor

### `/add_x_account <handle1> <handle2>...`
Adds Twitter accounts to track

### `/find_in_grok <query>`
Searches Grok AI for tweets

## Configuration

### Environment Variables
| Variable | Description |
|----------|-------------|
| `TELEGRAM_*` | Bot configuration |
| `TWITTER_*` | API v2 credentials |
| `GROK_API_*` | xAI integration |
| `REDIS_URL` | Cache server |

### Redis Keys
| Key | Purpose |
|-----|---------|
| `processed_articles` | Tracked URLs |
| `news_sites` | Monitored websites |
| `twitter_accounts` | Tracked handles |
| `processed_tweets` | Published tweets |

### Rate Limits
| Operation | Interval |
|-----------|---------|
| Telegram posts | 30s |
| Source checks | 10s |
| API retries | 5 attempts |
