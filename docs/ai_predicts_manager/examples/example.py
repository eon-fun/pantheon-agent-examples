import asyncio
from ai_predicts_manager.main import AsyncCryptoAISystem


async def main():
    system = AsyncCryptoAISystem("your_claude_key")

    await system.run_analysis(num_coins=3)

    btc_data = await system.data_collector.get_candle_data("BTC", "1h")
    analysis = await system.ai_analyzer.analyze_data([{
        "symbol": "BTC",
        "data": {"1h": btc_data}
    }])
    print(analysis)

asyncio.run(main())
