# API & Configuration Reference

## Core Components

### `DialogueManager` Class
- `handle()` - Main entry point
- `process_message()` - Stores messages
- `update_read_messages()` - Tracks read states
- `generate_summary()` - Creates AI summaries

### Telegram Commands
| Command | Description |
|---------|-------------|
| `/summary` | Generate conversation summary |

## Configuration

### Environment Variables
| Variable | Description |
|----------|-------------|
| `TELEGRAM_*` | API credentials |
| `OPENAI_API_KEY` | AI processing |
| `REDIS_URL` | Storage backend |

### Redis Keys
| Key | Purpose |
|-----|---------|
| `dialogue:messages` | Message storage |
| `dialogue:read_states` | Read tracking |

### AI Prompt
Customizable prompt in `AI_PROMPT` for controlling summary style and content focus.
