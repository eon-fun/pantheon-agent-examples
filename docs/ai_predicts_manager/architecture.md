# Architecture & Flow

## Overview
AsyncCryptoAISystem implements a complete market analysis pipeline with:

1. **Data Collection Layer**:
   - OHLCV candle data (1h, 4h, 1d)
   - Order book depth
   - Whale transaction tracking
   - Derivatives market data

2. **Analysis Layer**:
   - 20+ technical indicators
   - Market structure detection
   - Divergence analysis
   - Volume profile analysis

3. **AI Integration**:
   - Anthropic Claude processing
   - Trade idea generation
   - Risk assessment
   - Market commentary

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- Data collection components
- Analysis modules
- AI integration
- Redis caching layer

## Indicator Coverage
| Category | Indicators |
|----------|------------|
| Momentum | RSI, MACD, Stochastic |
| Volatility | ATR, Bollinger Bands |
| Volume | OBV, VWAP, Volume Profile |
| Structure | Pivot Points, Ichimoku, Swing Points |
