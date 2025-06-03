# Architecture & Flow

## Overview
The SolanaNewPairsBot is a distributed system that monitors Solana DEXs for new token pairs. It combines real-time data collection with automated alerting through Telegram, built on Ray Serve for horizontal scalability.

## Component Diagram
See [`architecture.puml`](./architecture.puml) for visualization of:

- Dextools API integration
- Solana RPC connections  
- PostgreSQL data storage
- Telegram bot messaging
- Ray Serve deployment topology

## Flow Description

### Data Collection Process
1. **Polling** (every 10 seconds):
   ```python
   while True:
       new_pairs = dextools.fetch_new_pairs()
       await process_pairs(new_pairs)
       await asyncio.sleep(10)
   ```
2. **Validation**:
   - Liquidity > $2,000
   - Contract verified
   - Not in blacklist
   - Age < 30 minutes

3. **Storage**:
   - Postgres schema includes:
     ```sql
     CREATE TABLE pairs (
         id SERIAL PRIMARY KEY,
         token_address VARCHAR(44) UNIQUE,
         pool_address VARCHAR(44),
         liquidity NUMERIC,
         detected_at TIMESTAMPTZ
     );
     ```

### Alert Generation
1. **Template Processing**:
   ```jinja2
   🚨 New {{ network }} Pair
   • Token: {{ token_address|truncate(6) }}
   • Liquidity: ${{ liquidity|thousands }}
   • 🔗 Trade: [Raydium]({{ raydium_link }})
   ```

2. **Rate Limiting**:
   - 3 messages/minute burst
   - 20 messages/hour sustained

### Failure Recovery
- **Database Outages**:
  ```python
  async def save_pair(pair):
      try:
          await db.insert(pair)
      except Exception:
          await redis.rpush('pending_pairs', pair)
  ```
- **Telegram Errors**:
  - Exponential backoff from 5s to 1h
  - Dead letter queue after 3 attempts

## Sequence Diagram
```plaintext
Dextools → Scanner → Validator → DB → Notifier → Telegram
     ↑----------- Retry Loop ------------↓
```

Key aspects matching your reference:
1. **Structured sections** (Overview, Diagram, Flow)
2. **Code snippets** showing critical logic
3. **Database schema** example
4. **Failure handling** details
5. **Plaintext diagram** alternative
6. **Technology specifics** without oversharing
7. **Architecture decisions** justification
