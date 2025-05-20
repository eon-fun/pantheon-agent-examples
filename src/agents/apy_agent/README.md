# DeFi APY Agent

An AI agent for finding the best and safest investment pools in DeFi protocols using the Enso Finance API.

## Features

- 🔍 Searches across multiple DeFi protocols for investment opportunities
- 💰 Finds pools with the best APY for a given token
- 🛡️ Implements safety checks to filter out risky or suspicious pools
- 📊 Provides detailed information about each pool
- 🤖 Simple Telegram interface for easy access

## Prerequisites

- Python 3.10+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Enso Finance API key

## Usage


```
In Telegram, send the following commands to your bot:
- `/start` - Get introduction and help
- `/help` - Show available commands
- `/find_pools <token_address>` - Find investment pools for a specific token

### Examples

Find pools for USDC:
```
/find_pools 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
```
Find pools for AAVE:
```
/find_pools 0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9
```

## Safety Checks

The bot implements multiple safety checks to help users avoid risky investments:

- APY Validation: Only shows pools with realistic APY (0.1% - 100%)
- Token Activity: Verifies all tokens in the pool have recent trading activity
- Price Checks: Ensures tokens have current, non-zero prices
- Protocol Verification: Checks for complete protocol information
- Data Freshness: Verifies price data is recent (within 24 hours)

## How It Works

1. User sends a token address to the bot
2. Bot queries the Enso Finance API for protocols that support the token
3. For each protocol, the bot finds pools that include the token
4. Safety checks are applied to filter out risky pools
5. Results are sorted by APY and presented to the user
6. Additional price information is fetched for context

## Architecture

- `APYAgent` class: Core functionality for interacting with Enso Finance API
- Aiogram integration: Provides Telegram bot interface
- Asynchronous processing: Handles pool searches efficiently

## API Integration

The bot uses the following Enso Finance API endpoints:
- `/api/v1/protocols`: To get the list of supported protocols
- `/api/v1/tokens`: To get DeFi tokens with APY information
- `/api/v1/prices/{chainId}/{tokenAddress}`: To get token price and activity information
