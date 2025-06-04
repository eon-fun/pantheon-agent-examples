# Solana New Pairs Tracking Bot

## Purpose & Scope
The SolanaNewPairsBot is an automated monitoring system designed to:

- Continuously scan for newly created token pairs on Solana DEXs
- Identify and analyze promising new trading opportunities
- Automatically publish findings to Telegram channels
- Provide real-time alerts and analytics

Key capabilities:
- Integration with Dextools API for comprehensive pair data
- SQL database storage for historical analysis
- Intelligent filtering of low-quality pairs
- Customizable alert templates

## Prerequisites

### Infrastructure Requirements
- **Solana RPC Node**: Mainnet endpoint (public or private)
- **PostgreSQL**: Version 12+ for data storage
- **Redis**: Optional for caching and queue management

### API Keys
| Service | Environment Variable | Example Value |
|---------|----------------------|---------------|
| Dextools | `DEXTOOLS_API_KEY` | `dt_xyz123...` |
| Telegram | `TG_BOT_TOKEN` | `123456:ABC...` |
| Solana | `SOLANA_RPC_URL` | `https://api.mainnet-beta.solana.com` |

### Python Requirements
- Python 3.10+ with virtualenv
- Core packages:
  ```text
  telethon==1.28.0
  sqlalchemy==2.0.0
  ray[serve]==2.5.0
  httpx==0.24.0
  ```

## Quickstart Guide

1. **Initial Setup**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configuration**
```bash
# Required variables
export DEXTOOLS_API_KEY="your_api_key_here"
export TG_BOT_TOKEN="123456:ABC..."
export SOLANA_RPC_URL="https://api.mainnet-beta.solana.com"

# Optional variables
export DB_URL="postgresql://user:pass@localhost:5432/solana_pairs"
export TG_CHANNEL_ID="@your_channel"
```

3. **Service Initialization**
```bash
# Start Ray cluster
ray start --head --port=6379

# Launch the agent
python -m solana_new_pairs_bot &> bot.log &
```

4. **Verification**
```bash
# Check service health
curl http://localhost:8000/health

# View active tasks
ray status
