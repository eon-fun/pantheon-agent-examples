# API & Configuration Reference

## Core Methods

### `run_analysis(num_coins=5)`
Main analysis loop (continuous operation)

### `analyze_data(market_data)`
Process raw market data through AI

### `integrate_analysis(candles, order_book)`
Comprehensive technical analysis

## Configuration

### Environment Variables
| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Claude API access |
| `REDIS_URL` | Results caching |
| `MARKET_DATA_*` | Data provider config |

### Analysis Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `num_coins` | 5 | Top coins to analyze |
| `timeframes` | 1h,4h,1d | Analysis periods |
| `interval` | 300s | Analysis frequency |

## Output Format
```json
{
  "trade_alerts": [{
    "symbol": "BTC",
    "type": "long",
    "entry": "42000-42200",
    "targets": ["42500", "43000"],
    "stop": "41800",
    "risk_reward": 2.5,
    "thesis": "Bullish RSI divergence",
    "risk_level": "medium"
  }],
  "market_alpha": {
    "structure": "Bullish higher lows",
    "smart_money": "Accumulating at support",
    "key_levels": {
      "BTC": {
        "support": ["42000", "41500"],
        "resistance": ["42500", "43000"]
      }
    }
  }
}
