# API & Configuration Reference

## REST API Endpoints

### `POST /{goal}`
Initiates gorilla marketing campaign for specified goal.

#### URL Parameters
| Parameter | Format | Example | Description |
|-----------|--------|---------|-------------|
| `goal` | `username.keywords.themes` | `nfinityAI.web3,ai.decentralized` | Triple-segment goal string |

#### Goal Structure
1. **Username**: Twitter handle to post from
2. **Keywords**: Comma-separated search terms (e.g., `web3,ai`)
3. **Themes**: Comma-separated discussion topics (e.g., `decentralized,autonomous_agents`)

#### Request Body
```json
{
   "plan": {
      "max_comments": 2,
      "min_likes": 5,
      "delay_between_posts": 300
   }
}
```

## Configuration

### Redis Tracking
```python
# Keys structure:
"gorilla_marketing_answered:{username}"  # Set of commented tweet IDs
"user_posts:{username}"                 # Sorted set of all posts
```

### Rate Limiting
```python
@ensure_delay_between_posts
async def post_comment():
    # Enforces minimum 5 minutes between comments
```

## Response Handling

### Success
```json
{
  "status": "completed",
  "comments_posted": 2,
  "last_tweet_id": "1234567890"
}
```

### Error Cases
```json
{
  "error": "no_relevant_tweets",
  "message": "No tweets matching safety criteria"
}
```
