from datetime import datetime

from database.redis.redis_client import db


def view_signal_history():
    """Просмотр истории сигналов в Redis"""
    print("\n=== Signal History ===")

    try:
        # Получаем размер множества
        set_size = db.r.zcard("trading_signals")
        print(f"Total signals in Redis set: {set_size}")

        # Получаем все сигналы без ограничений
        signals = db.r.zrange("trading_signals", 0, -1, withscores=True, desc=True)
        print(f"Retrieved signals from Redis: {len(signals)}")

        signals_with_time = []

        for signal in signals:
            try:
                signal_str = signal[0].decode("utf-8")  # symbol:direction:timestamp
                timestamp = signal[1]  # score from sorted set

                # Разбираем ключ сигнала
                symbol, direction, _ = signal_str.split(":")
                date_str = datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")

                signals_with_time.append(
                    {"symbol": symbol, "direction": direction, "timestamp": date_str, "raw_timestamp": timestamp}
                )

            except Exception as e:
                print(f"Error processing signal {signal}: {str(e)}")
                continue

        # Выводим в формате таблицы
        print(f"\n{'Time':^20} | {'Symbol':^6} | {'Signal':^8}")
        print("-" * 38)

        for signal in signals_with_time:
            print(f"{signal['timestamp']:20} | {signal['symbol']:^6} | {signal['direction']:^8}")

        print(f"\nTotal processed signals: {len(signals_with_time)}")

        # Дополнительная статистика
        symbols = set(s["symbol"] for s in signals_with_time)
        for symbol in symbols:
            symbol_signals = [s for s in signals_with_time if s["symbol"] == symbol]
            up_signals = sum(1 for s in symbol_signals if s["direction"] == "UP")
            down_signals = sum(1 for s in symbol_signals if s["direction"] == "DOWN")
            print(f"\n{symbol} statistics:")
            print(f"Total signals: {len(symbol_signals)}")
            print(f"UP signals: {up_signals}")
            print(f"DOWN signals: {down_signals}")

    except Exception as e:
        print(f"Error viewing signal history: {str(e)}")


if __name__ == "__main__":
    view_signal_history()
