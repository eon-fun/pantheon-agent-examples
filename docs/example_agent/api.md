# API & Configuration Reference

## REST Endpoints

### `POST /{goal}`
Executes a workflow for the specified goal.

#### Request Body
```json
{
  "workflow": {
    "steps": [],
    "parameters": {}
  },
  "context": {}
}
```

#### Responses
**Success (200):**
Returns processed workflow results

## Configuration Reference

### Environment Variables
| Variable | Description |
|----------|-------------|
| `RAY_ADDRESS` | Ray cluster address |
| `AGENT_CONFIG_PATH` | Custom config path |

### Bootstrap Process
1. Loads base configuration
2. Initializes Ray Serve
3. Binds agent with config
4. Starts HTTP server
