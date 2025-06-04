# API & Configuration Reference

## Public Endpoint

### `POST /{goal}`

Triggers the Twitter liking behavior for a given user and goal definition.

#### Path Parameters

- `goal` — a dot-delimited string composed of:
  - **Username** — the Twitter username to act as (e.g. `myuser`)
  - **Keywords** — one or more search terms (e.g. `python-ai`)
  - **Themes** — one or more theme tags (e.g. `startup-research`)

**Example:**
```
POST /myuser.python-ai.startup-research
```

#### Request Body

The request body is optional and may include a `plan` dictionary (currently unused):

```json
{
  "plan": {
    "like_limit": 3
  }
}
```

#### Behavior

- Parses the goal string into username, keywords, and themes.
- Uses `tweetscout_utils.search_tweets` to find tweets.
- Filters tweets already liked (stored in Redis).
- Likes 1–3 random tweets not previously liked.
- Tracks newly liked tweet IDs in Redis.

#### Response

Returns HTTP 200 OK on completion. No body is returned.

---

## Configuration Reference

### Redis Keys

- `user_likes:{username}` — Redis Set storing tweet IDs liked by the user.

### Required Environment Variables

| Variable                 | Description                            |
|--------------------------|----------------------------------------|
| `TWITTER_CLIENT_ID`      | Twitter OAuth client ID                |
| `TWITTER_CLIENT_SECRET`  | Twitter OAuth client secret            |
| Redis credentials        | Used implicitly by `get_redis_db()`    |

All environment variables are assumed to be managed securely outside the code.
