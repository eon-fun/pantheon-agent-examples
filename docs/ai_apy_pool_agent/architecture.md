# Architecture & Flow

## Overview

APYAgent is a Telegram bot built with `aiogram` that interacts with the Enso Finance API to find and recommend secure DeFi investment pools for a given token address. It validates pools based on safety criteria and returns a formatted recommendation via Telegram.

## Component Diagram

See [`architecture.puml`](./architecture.puml) for a high-level sequence diagram, including:
- Telegram User interacting with the bot
- APYAgent Bot processing requests
- Enso Finance API as the external data source
- Redis (not used in the current implementation but included for potential caching)

## Flow Description

1. **User sends `/find_pools <token_address>`** via Telegram.
2. The bot:
   - Validates the provided token address.
   - Queries the Enso Finance API to retrieve a list of supported protocols.
   - For each protocol:
     - Fetches DeFi tokens for the specified chain (default: `chainId=1`).
     - Filters tokens containing the provided `token_address` in their underlying tokens.
     - Retrieves price data for underlying tokens to ensure they are active.
     - Validates each pool based on safety criteria:
       - APY between 0.1% and 100%.
       - At least two underlying tokens.
       - All required fields (`chainId`, `address`, `decimals`, `type`, `protocolSlug`).
       - Active underlying tokens with valid, recent prices.
   - Selects the pool with the highest APY and up to five alternatives.
   - Formats a Markdown recommendation with pool details (APY, protocol, token addresses, etc.).
3. The bot sends the recommendation back to the user via Telegram.

