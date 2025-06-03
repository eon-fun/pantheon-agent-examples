# API & Configuration Reference

## Public Commands
### `/summary`
Generates a digest of all collected messages since last cleanup.

**Behavior**:
1. Triggers message cleanup (removes read messages)
2. Combines remaining messages into a prompt
3. Sends to OpenAI with this system prompt:
```text
You are an assistant summarizing messages in a chat...
[Full prompt from PROMPT constant]
```
4. Returns formatted summary

**Response Example**:
```text
📋 Summary:

[Work Chat] @john mentioned: Need help with the Q3 report
[Family Group] @mom replied: Dinner at 7pm tonight
[Project Channel] @alex wrote: Updated the design mockups
```

## Configuration

### Redis Keys
| Key | Format | Description |
|-----|--------|-------------|
| `telegram_messages` | Sorted Set | Stores messages with timestamp as score |

### Environment Variables
| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `API_ID` | Yes | `123456` | Telegram API ID from my.telegram.org |
| `API_HASH` | Yes | `a1b2c3...` | Telegram API hash |
| `OPENAI_API_KEY` | Yes | `sk-...` | OpenAI API key |

### Constants (in code)
| Name | Default | Description |
|------|---------|-------------|
| `SESSION_NAME` | `"my_telegram_session"` | Telethon session filename |
| `REDIS_MESSAGES_KEY` | `"telegram_messages"` | Redis storage key |
| `BOT_COMMAND` | `"/summary"` | Trigger command |

## Data Structures
**Message Storage Format** (JSON in Redis):
```json
{
  "id": "message_id",
  "text": "message content",
  "sender_username": "@username",
  "action": "wrote|mentioned|replied",
  "chat_name": "Chat Title",
  "chat_id": 123456789,
  "timestamp": 1620000000.0
}
```

## Error Handling
- Failed API calls will return user-friendly messages
- Redis errors trigger fallback to memory storage
- Telegram auth failures provide step-by-step recovery
