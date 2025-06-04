# API & Configuration Reference

## REST API Endpoints

### POST `/control/start`
Initiates message listening on the specified Telegram channel.

**Response:**
- `202 Accepted`: Listener start requested
- `503 Service Unavailable`: Data processing backend not initialized

**Example:**
```bash
curl -X POST http://localhost:8000/control/start
```

### POST `/control/stop`
Gracefully stops the message listener.

**Response:**
- `202 Accepted`: Listener stop requested

**Example:**
```bash
curl -X POST http://localhost:8000/control/stop
```

### GET `/control/status`
Returns current agent status.

**Response:**
```json
{
  "status": "running|stopping|stopped",
  "client_connected": true|false,
  "phone": "+1234567890",
  "target_chat": "-1001234567890"
}
```

**Example:**
```bash
curl http://localhost:8000/control/status
```

## Configuration Reference

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `TELEGRAM_PHONE_NUMBER` | Yes | Telegram account number in international format | `"+1234567890"` |
| `TARGET_CHAT_ID` | Yes | Numeric chat ID or username | `-1001234567890` or `"channelname"` |

### Error Handling
The agent automatically handles:
- Connection drops (auto-reconnect)
- Flood wait restrictions
- Authentication errors
- Permission issues

## Message Processing Flow
1. New message event received
2. Message passed to `process_new_message()`
3. Data validation and transformation
4. Output to configured processing pipeline
