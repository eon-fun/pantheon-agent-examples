# WalletTrackingAgent

## Purpose & Scope
WalletTrackingAgent monitors blockchain wallets for transactions by:
- Tracking specified wallet addresses across multiple chains
- Detecting buy/sell transactions
- Formatting transaction alerts
- Maintaining processed transaction history

## Prerequisites
- Python 3.10+
- Ray framework
- Redis server
- Ankr RPC API key
- Telegram bot (optional for notifications)
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `ANKR_API_KEY` - Ankr RPC API key
- `REDIS_URL` - Redis connection string
- `TELEGRAM_BOT_TOKEN` - Optional for notifications

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Ray:**
   ```bash
   ray start --head
   ```

3. **Run the agent:**
   ```python
   wallet_agent = WalletTrackingAgent.remote()
   ray.get(wallet_agent.process_wallets.remote())
   ```

4. **Manage wallets:**
   ```python
   # Add wallet
   ray.get(wallet_agent.add_wallet.remote("0x..."))

   # Remove wallet
   ray.get(wallet_agent.remove_wallet.remote("0x..."))
   ```

**Key Features:**
- Multi-chain support (Ethereum, BSC, Polygon, etc.)
- Buy/sell detection
- Transaction deduplication
- Rich message formatting
