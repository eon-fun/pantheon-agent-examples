# API & Configuration Reference

## Public API Endpoint

### `POST /{goal}`
Triggers tweet generation pipeline.

#### Request Format
```
username.keyword1,keyword2.theme1,theme2
```

#### Parameters
| Component    | Description                          | Example               |
|--------------|--------------------------------------|-----------------------|
| username     | Twitter handle to post as            | `cryptodev`           |
| keywords     | Comma-separated content focus terms  | `defi,web3,staking`   |
| themes       | Comma-separated hashtag categories   | `crypto,blockchain`   |

#### Response
```json
{
  "status": "posted|queued|failed",
  "tweet_id": "1234567890",
  "content": "Generated tweet text...",
  "type": "regular|news|quote"
}
```

## Content Generation Rules

### Prompt Templates
1. **Regular Tweets** (`PROMPT_FOR_TWEET`):
   - Max 260 characters
   - Double line breaks between thoughts
   - Strictly no emojis/hashtags

2. **Quote Tweets** (`PROMPT_FOR_QUOTED_TWEET`):
   - Comments on existing tweets
   - Adds original insights
   - Maintains conversational flow

3. **News Summaries** (`PROMPT_FOR_NEWS_TWEET`):
   - Aggregates multiple sources
   - Provides neutral analysis
   - Links to project themes

## Configuration
```python
# Content formatting rules
MAX_LENGTH = 260
PARAGRAPH_BREAKS = True
ALLOWED_CONTENT_TYPES = ["regular", "news", "quote"]
```