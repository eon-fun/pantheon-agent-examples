# Architecture & Flow

## Overview
WalletTrackingAgent implements blockchain monitoring with:

1. **Data Collection**:
   - Ankr RPC API integration
   - Multi-chain transaction queries
   - Hex-to-decimal conversion

2. **Processing**:
   - Buy/sell classification
   - Amount normalization (wei to ETH)
   - Duplicate detection

3. **Storage**:
   - Redis-backed wallet tracking
   - Processed transaction cache
   - Set operations for management

## Component Diagram
See [`architecture.puml`](./architecture.puml) showing:
- Ray distributed execution
- Ankr API integration
- Redis data management
- Multi-chain support

## Transaction Flow
1. Wallet address validation
2. API request to Ankr
3. Response processing
4. Transaction classification
5. Result formatting
