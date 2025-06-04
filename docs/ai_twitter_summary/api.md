# API & Configuration Reference

## Core Components

### `TweetProcessor` Class
- `fetch_tweets(account)` - Gets new tweets for an account
- `process_new_tweets()` - Checks all monitored accounts
- `get_redis_set_items(key)` - Helper for Redis access

### Supporting Functions
- `summarize_tweets(tweets)` - Generates AI summaries
- `periodic_task()` - Main processing loop

## Configuration

### Environment Variables
| Variable | Description |
|----------|-------------|
| `TWITTER_BEARER_TOKEN` | API v2 bearer token |
| `TELEGRAM_*` | Bot configuration |
| `OPENAI_API_KEY` | AI processing |
| `REDIS_URL` | State management |

### Redis Keys
| Key | Purpose |
|-----|---------|
| `subscribed_twitter_accounts` | Tracked handles |
| `last_processed_tweets` | Published tweet IDs |

### AI Prompt
Customizable prompt in `AI_PROMPT` constant for controlling summary style and content focus.
