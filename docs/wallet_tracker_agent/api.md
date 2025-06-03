# API & Configuration Reference

## Core Methods

### `check_wallet_transactions(wallet_address)`
Fetches transactions for a wallet

### `add_wallet(wallet_address)`
Adds wallet to monitoring list

### `remove_wallet(wallet_address)`
Removes wallet from monitoring

### `process_wallets()`
Main processing loop

## Configuration

### Environment Variables
| Variable | Description |
|----------|-------------|
| `ANKR_API_KEY` | Ankr RPC endpoint key |
| `REDIS_URL` | Redis server URL |

### Redis Keys
| Key | Purpose |
|-----|---------|
| `watched_wallets` | Tracked addresses |
| `processed_transactions:{wallet}` | Processed TX hashes |

### Message Format
```
🟢/🔴 Transaction Alert

🔗 Wallet: 0x...
⛓️ Chain: eth
💱 Action: Buy/Sell
🪙 Token: ETH
📊 Amount: 1.5
💵 Price: $2000

[View TX](explorer_url)
