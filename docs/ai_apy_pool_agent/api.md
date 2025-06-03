# API & Configuration Reference

## Public Interface

APYAgent is a Telegram bot and does not expose a traditional REST API. Instead, it provides Telegram commands that interact with the Enso Finance API to process user requests. The primary command is documented below.

### `/find_pools <token_address>`

Initiates a search for secure DeFi investment pools for the specified token address.

#### Parameters

- `token_address` — The Ethereum token address to search for (e.g., `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`)

**Example:**

```bash
/find_pools 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
```
#### Behavior

- Validates the provided token address.
- Queries the Enso Finance API for supported protocols and DeFi tokens.
- Filters pools based on safety criteria:
  - APY between 0.1% and 100%.
  - Active underlying tokens with valid prices.
  - Presence of required fields (`chainId`, `address`, `decimals`, `type`, `protocolSlug`).
  - At least two underlying tokens.
- Returns a formatted recommendation with the best pool and up to five alternatives, including APY, protocol, and token details.

#### Response

Returns a Markdown-formatted message in Telegram with pool details or an error message if no pools are found or an error occurs.

**Example Response:**

----
🏆 *Finded pools for investment:*

• *ProtocolA*:
  - APY: 5.20%
  - Pool type: staking
  - Contract: `0x...`

📊 *Description of best pool:*
- Protocol: ProtocolA
- APY: 5.20%
- Type: `staking`
- Pool address: `0x...`
- Contract: `0x...`

💰 *Tokens in pool:*
    - USDC: $1.00
    - ETH: $3,500.00
---

## Configuration Reference

### Required Environment Variables

| Variable              | Description                              |
|-----------------------|------------------------------------------|
| `TELEGRAM_BOT_TOKEN`  | Telegram Bot API token for bot operation |
| `ENSO_API_KEY`        | Enso Finance API key for DeFi data access|

All environment variables must be set securely before running the bot.

### Configuration Example

```bash
export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
export ENSO_API_KEY="your-enso-api-key"
```