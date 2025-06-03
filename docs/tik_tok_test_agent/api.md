# API Reference

## Endpoints

### POST `/{goal}`
Main endpoint for triggering TikTok comment operations.

#### Parameters
- `goal` (path): Action type (currently only "comment" supported)
- `plan` (body, optional): Additional parameters (not currently used)

#### Example Request
```bash
curl -X POST http://localhost:8000/comment
```

#### Response
Successful response:
```json
{
    "success": true
}
```

Error response:
```json
{
    "success": false,
    "error": "Error message"
}
```

## Execution Flow
1. Installs Chrome (if not present)
2. Initializes TikTokBot with 2captcha API key
3. Logs into TikTok using credentials
4. Posts comment to hardcoded test video
5. Closes browser session

## Configuration Keys
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headless` | bool | `False` | Run browser in headless mode |
| `api_key` | str | - | 2captcha service API key |
| `video_url` | str | Test URL | Target TikTok video URL |
| `comment_text` | str | "Hello world!_test_test" | Comment to post |

## Error Handling
Common error scenarios:
- Chrome installation failures
- TikTok login failures
- Captcha solving timeouts
- Invalid video URLs
- Rate limiting from TikTok