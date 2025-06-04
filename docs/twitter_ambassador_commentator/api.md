# API & Configuration Reference

## Public Endpoint

### `POST /{goal}`

Triggers the Twitter commenting behavior for a given user and project.

#### Path Parameters

- `goal` — a dot-delimited string composed of:
  - **MyUsername** — the Twitter username acting as commentator (e.g. `myuser`)
  - **ProjectUsername** — the Twitter username of the project to comment on (e.g. `projectuser`)

**Example:**
```

POST /myuser.projectuser

````

#### Request Body

The request body is optional and may include a `plan` dictionary (currently unused):

```json
{
  "plan": {}
}
````

#### Behavior

* Parses the goal string into `my_username` and `project_username`.
* Retrieves Twitter access token for `my_username`.
* Fetches recent tweets from `project_username` using `tweetscout_utils.fetch_user_tweets`.
* Checks Redis for tweets already commented on.
* Generates a positive, human-like comment for the first un-commented tweet using OpenAI via `create_comment_to_post`.
* Posts the comment tweet as a reply to the original tweet.
* Stores the posted comment and tweet IDs in Redis to avoid duplicates.
* Enforces delay between posts using Redis-based rate limiting.

#### Response

Returns HTTP 200 OK on successful comment posting, or a message if no new tweets are available to comment on.

---

## Configuration Reference

### Redis Keys

* `commented_tweets:{my_username}:{project_username}` — Redis Set storing IDs of tweets already commented on by `my_username` for `project_username`.
* User posts are saved with details including post ID, text, sender username, timestamp, and reply-to tweet ID.

### Required Environment Variables

| Variable                | Description                         |
| ----------------------- | ----------------------------------- |
| `TWITTER_CLIENT_ID`     | Twitter OAuth client ID             |
| `TWITTER_CLIENT_SECRET` | Twitter OAuth client secret         |
| Redis credentials       | Used implicitly by `get_redis_db()` |

Environment variables are expected to be securely managed externally.
