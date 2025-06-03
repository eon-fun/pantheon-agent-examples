# AsyncCryptoAISystem

## Purpose & Scope
AsyncCryptoAISystem provides comprehensive cryptocurrency market analysis by:
- Collecting real-time market data from multiple sources
- Performing advanced technical analysis
- Generating AI-powered trading insights
- Identifying market structure and key levels
- Detecting whale activity and order flow patterns

## Prerequisites
- Python 3.10+
- Anthropic Claude API access
- Cryptocurrency market data API access
- Redis for caching and state management
- Dependencies from PyPI (listed in `requirements.txt`)

### Required Environment Variables
- `ANTHROPIC_API_KEY` - Anthropic Claude API key
- `REDIS_URL` - Redis connection string
- `MARKET_DATA_API_KEY` - Cryptocurrency data provider key

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export ANTHROPIC_API_KEY="your_claude_key"
   export REDIS_URL="redis://localhost:6379"
   ```

3. **Run the system:**
   ```python
   from async_crypto_ai_system import AsyncCryptoAISystem
   system = AsyncCryptoAISystem("your_claude_key")
   asyncio.run(system.run_analysis())
   ```

**Key Features:**
- Multi-timeframe technical analysis
- AI-generated trade ideas
- Market structure identification
- Risk metric calculation
- Continuous monitoring
