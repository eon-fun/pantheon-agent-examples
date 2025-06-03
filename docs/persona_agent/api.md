# API & Configuration Reference

## REST Endpoints

### `POST /{persona_name}`
Generates text in the specified persona's style.

#### Request Body
```json
{
  "prompt": "your generation instruction",
  "plan": {"optional": "generation plan"}
}
```

#### Responses
**Success (200):**
```json
{
  "success": true,
  "result": "generated text in persona style"
}
```

**Error (400):**
```json
{
  "success": false,
  "result": "error message"
}
```

## Configuration Reference

### Environment Variables
| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `REDIS_URL` | Redis connection URL |
| `QDRANT_URL` | Qdrant server URL |
| `QDRANT_API_KEY` | Qdrant API key (optional) |

### Example Configuration
```bash
export OPENAI_API_KEY="sk-your-key"
export REDIS_URL="redis://user:pass@host:port"
export QDRANT_URL="https://your-qdrant-host"
```

## Data Requirements
1. **Redis** must contain:
   - `{persona_name}:description` - Persona description
2. **Qdrant** must have:
   - Collection matching `persona_name`
   - Tweet embeddings stored with text payloads
