# API Reference

## Core Endpoints

### `POST /{command}`
Triggers specific bot operations. The following commands are supported:

| Command | Description | Parameters |
|---------|-------------|------------|
| `scan` | Force immediate chain scan | `{"interval": "5m", "chains": ["solana"]}` |
| `post` | Manual Telegram posting | `{"test_mode": true}` |
| `stats` | Generate market statistics | `{"timeframe": "24h"}` |

**Example Request:**
```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"interval": "10m", "priority": "high"}'
```

**Response Schema:**
```json
{
  "status": "success|error",
  "data": {
    "new_pairs": 5,
    "posted_alerts": 3,
    "scan_duration": "12.7s"
  },
  "timestamp": "2023-11-15T14:32:10Z"
}
```

## Data Collection API

### Dextools Integration
```yaml
base_url: https://api.dextools.io/v1
endpoints:
  new_pairs: /pairs/solana/new
  pair_details: /pair/solana/{address}
rate_limit: 10 requests/minute
```

### Solana RPC Methods
Required methods:
- `getProgramAccounts` (Token Program)
- `getAccountInfo`
- `getTransaction`

## Alert Configuration

### Telegram Post Template
```jinja
🚀 *New {{ network }} Pair Detected!*

• Token: `{{ token_address }}`
• Pool: `{{ pool_address }}`
• Liquidity: ${{ liquidity|format_number }}
• Age: {{ age }} minutes

{% if is_verified %}✅ Verified Project{% endif %}
```

### Filtering Rules
```python
MIN_LIQUIDITY = 2000  # USD
MAX_AGE = 30  # minutes
BLACKLIST = ["0x123...def"]  # scam tokens
```


### Key Features:
1. **Command-Specific Documentation** - Clear table of available commands
2. **Live Examples** - Ready-to-use cURL commands
3. **Response Schema** - Detailed output structure
4. **Integration Specs** - API rate limits and endpoints
5. **Template Examples** - Customizable alert formats

### Usage Notes:
- All endpoints require `Content-Type: application/json`
- Error responses include `retry-after` header when rate-limited
- Commands are queued and processed asynchronously
