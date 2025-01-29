from database.redis.redis_client import db
from datetime import datetime
import json


def view_signal_history():
    """Просмотр истории сигналов в Redis"""
    print("\n=== Signal History ===")

    # Получаем все сигналы с временными метками
    signals_with_time = []

    # Используем ZRANGE с WITHSCORES для получения значений и их score
    signals = db.r.zrange('trading_signals', 0, -1, withscores=True, desc=True)

    for signal in signals:
        signal_str = signal[0].decode('utf-8')  # BTC:UP или ETH:DOWN
        timestamp = int(signal[1])  # берем целую часть timestamp

        symbol, direction = signal_str.split(':')
        date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        signals_with_time.append({
            'symbol': symbol,
            'direction': direction,
            'timestamp': date_str
        })

    # Выводим в формате таблицы
    print(f"{'Time':^20} | {'Symbol':^6} | {'Signal':^6}")
    print("-" * 36)

    for signal in signals_with_time:
        print(f"{signal['timestamp']:20} | {signal['symbol']:^6} | {signal['direction']:^6}")

    print(f"\nTotal signals in history: {len(signals_with_time)}")


if __name__ == "__main__":
    view_signal_history()
