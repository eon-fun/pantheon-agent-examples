# API & Configuration Reference

## Public Interface

AIAvatar is a Telegram bot and does not expose a traditional REST API. Instead, it provides Telegram commands and message handling to interact with users, leveraging the OpenAI API for responses and Redis for context storage. The primary command is documented below.

### `/new_style`

Refreshes the user’s messaging style context by fetching their last 100 messages from Telegram chats.

#### Parameters

None

**Example:**

```bash
/new_style
```

#### Behavior

- Fetches up to 100 recent messages sent by the user across different Telegram chats.
- Stores the messages in Redis under the user’s ID for style analysis.
- Responds with a confirmation message or an error if the operation fails.

#### Response

Returns a Telegram message confirming success or reporting an error.

**Example Response:**

```markdown
Context successfully updated!
```

### Message Handling

Handles any incoming user message (excluding commands) by generating a conversational response.

#### Parameters

- User message (free-form text sent to the bot)

**Example:**

```bash
Hey, what's up? Can you help me with some Python tips?
```

#### Behavior

- Retrieves up to 100 recent user messages for style analysis.
- Loads the last bot response from Redis (if available) for context.
- Sends a prompt to the OpenAI API, including the user’s recent messages, the last bot response, and the current message.
- Generates a response matching the user’s tone and style.
- Stores the response in Redis for future context.
- Sends the response to the user via Telegram.

#### Response

Returns a Telegram message with a conversational response or an error message if processing fails.

**Example Response:**

```markdown
Yo, what's good? Sure thing, I can drop some Python tips! Want help with a specific topic, like loops or async stuff?
```

---

## Configuration Reference

### Redis Keys

- `user:<user_id>` — Stores the user’s recent messages and last bot response for context.

### Required Environment Variables

| Variable             | Description                                      |
|---------------------|--------------------------------------------------|
| `API_ID`            | Telegram API ID from my.telegram.org             |
| `API_HASH`          | Telegram API Hash from my.telegram.org          |
| `OPENAI_API_KEY`    | OpenAI API key for conversational responses     |
| `REDIS_HOST`        | Redis host address                              |
| `REDIS_PORT`        | Redis port (e.g., 6379)                         |
| `REDIS_DB`          | Redis database index (e.g., 0)                  |

### Configuration Example

```bash
export API_ID="your-telegram-api-id"
export API_HASH="your-telegram-api-hash"
export OPENAI_API_KEY="your-openai-api-key"
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_DB="0"
```