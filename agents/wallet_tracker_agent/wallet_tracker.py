import asyncio
import sys
from dataclasses import dataclass

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from database.redis.redis_client import RedisDB


@dataclass
class Transaction:
    wallet: str
    type: str  # buy/sell
    token: str
    amount: float
    timestamp: int
    hash: str
    chain: str
    price: float | None = None


def hex_to_decimal(hex_string: str, base_type: str = "value") -> float:
    """Конвертация hex значения в decimal

    Args:
        hex_string: Hex строка для конвертации
        base_type: Тип значения ('value' или 'timestamp')

    """
    if not hex_string.startswith("0x"):
        return float(hex_string)
    try:
        dec_value = int(hex_string, 16)
        if base_type == "value":
            return float(dec_value)
        return dec_value  # для timestamp возвращаем int
    except ValueError:
        return 0.0


# Инициализация Redis
db = RedisDB()
WATCHED_WALLETS_KEY = "watched_wallets"
PROCESSED_TXS_KEY = "processed_transactions"

# Telegram конфигурация
TELEGRAM_BOT_TOKEN = "7633131821:AAForOPCLS045IFHihMf49UozGwKL7IMbpU"
TELEGRAM_CHANNEL_ID = "@pantheoncryptotest"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# API конфигурация
ANKR_API_KEY = "0edb7f866074ee92aa1c799f1829524801c36af92624abaaa8ba5517b98104f4"
ANKR_API_URL = f"https://rpc.ankr.com/multichain/{ANKR_API_KEY}"

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def check_wallet_transactions(wallet_address: str) -> list[Transaction]:
    """Получение транзакций через Ankr RPC API"""
    processed_txs = set(db.get_set(f"{PROCESSED_TXS_KEY}:{wallet_address}"))
    transactions = []

    payload = {
        "jsonrpc": "2.0",
        "method": "ankr_getTransactionsByAddress",
        "params": {
            "address": wallet_address,
            "blockchain": ["eth", "bsc", "polygon", "arbitrum", "optimism"],
            "pageSize": 50,
            "pageToken": "",
            "fromBlock": "latest",
        },
        "id": 1,
    }

    headers = {"Content-Type": "application/json"}

    try:
        print(f"Отправка запроса к Ankr RPC API для кошелька {wallet_address}")
        print(f"Payload: {payload}")

        async with aiohttp.ClientSession() as session:
            async with session.post(ANKR_API_URL, headers=headers, json=payload, timeout=30) as response:
                response_text = await response.text()
                print(f"Получен ответ от API. Статус: {response.status}")
                print(f"Текст ответа: {response_text[:500]}...")

                if response.status != 200:
                    print(f"Ошибка API статус {response.status}: {response_text}")
                    return []

                try:
                    data = await response.json()
                    print("Данные успешно распарсены")
                except ValueError as e:
                    print(f"Ошибка парсинга JSON: {e}\nОтвет: {response_text}")
                    return []

                if "error" in data:
                    print(f"Ошибка API: {data['error']}")
                    return []

                transactions_data = data.get("result", {}).get("transactions", [])
                print(f"Получено {len(transactions_data)} транзакций")

                for tx in transactions_data:
                    tx_hash = tx.get("hash")
                    if tx_hash in processed_txs:
                        print(f"Транзакция {tx_hash} уже обработана")
                        continue

                    try:
                        # Конвертируем hex значения в decimal
                        value = hex_to_decimal(tx.get("value", "0x0"), "value")
                        timestamp = hex_to_decimal(tx.get("timestamp", "0x0"), "timestamp")

                        transaction = Transaction(
                            wallet=wallet_address,
                            type="buy" if tx.get("to", "").lower() == wallet_address.lower() else "sell",
                            token=tx.get("currency", {}).get("symbol", "ETH"),
                            amount=value / (10**18),  # Конвертация из Wei в ETH
                            timestamp=timestamp,
                            hash=tx_hash,
                            chain=tx.get("blockchain", "eth"),
                        )
                        transactions.append(transaction)
                        print(f"Добавлена новая транзакция: {transaction}")
                    except Exception as e:
                        print(f"Ошибка при обработке транзакции {tx}: {e}")

    except Exception as e:
        print(f"Ошибка при получении транзакций для {wallet_address}: {e}")

    return transactions


def format_transaction_message(tx: Transaction) -> str:
    """Форматирование данных транзакции для сообщения"""
    action_emoji = "🟢" if tx.type == "buy" else "🔴"
    chain_urls = {
        "eth": "etherscan.io",
        "polygon": "polygonscan.com",
        "bsc": "bscscan.com",
        "arbitrum": "arbiscan.io",
        "optimism": "optimistic.etherscan.io",
    }

    explorer_url = f"https://{chain_urls.get(tx.chain, 'etherscan.io')}/tx/{tx.hash}"

    return (
        f"{action_emoji} Транзакция на кошельке\n\n"
        f"🔗 Кошелек: `{tx.wallet}`\n"
        f"⛓️ Сеть: `{tx.chain}`\n"
        f"💱 Действие: {action_emoji} {'Покупка' if tx.type == 'buy' else 'Продажа'}\n"
        f"🪙 Токен: `{tx.token}`\n"
        f"📊 Количество: `{tx.amount}`\n"
        f"💵 Цена: `${tx.price if tx.price else 'н/д'}`\n\n"
        f"[Посмотреть транзакцию]({explorer_url})"
    )


@dp.message(Command("add_wallet"))
async def add_wallet(message: Message):
    """Обработчик команды добавления кошелька"""
    try:
        wallet = message.text.split()[1]
        if len(wallet) != 42 or not wallet.startswith("0x"):
            await message.reply("❌ Некорректный адрес кошелька. Укажите правильный адрес.")
            return

        db.add_to_set(WATCHED_WALLETS_KEY, wallet)
        await message.reply(f"✅ Кошелек {wallet} добавлен в список отслеживания!")
    except IndexError:
        await message.reply("❌ Укажите адрес кошелька после команды.")


@dp.message(Command("list_wallets"))
async def list_wallets(message: Message):
    """Показать список отслеживаемых кошельков"""
    wallets = db.get_set(WATCHED_WALLETS_KEY)
    if not wallets:
        await message.reply("📝 Список отслеживаемых кошельков пуст")
        return

    wallet_list = "\n".join([f"• `{w}`" for w in wallets])
    await message.reply(f"📝 Отслеживаемые кошельки:\n{wallet_list}")


@dp.message(Command("remove_wallet"))
async def remove_wallet(message: Message):
    """Удалить кошелек из отслеживания"""
    try:
        wallet = message.text.split()[1]
        db.r.srem(WATCHED_WALLETS_KEY, wallet)
        await message.reply(f"✅ Кошелек {wallet} удален из списка отслеживания")
    except IndexError:
        await message.reply("❌ Укажите адрес кошелька после команды")


async def monitor_wallets():
    """Основной цикл мониторинга кошельков"""
    while True:
        try:
            wallets = db.get_set(WATCHED_WALLETS_KEY)
            print(f"Отслеживаемые кошельки: {wallets}")

            for wallet in wallets:
                print(f"Проверка транзакций для кошелька: {wallet}")
                transactions = await check_wallet_transactions(wallet)
                print(f"Найдено транзакций: {len(transactions)}")

                for tx in transactions:
                    message = format_transaction_message(tx)
                    await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode="Markdown")
                    db.add_to_set(f"{PROCESSED_TXS_KEY}:{wallet}", tx.hash)
                    print(f"Отправлено сообщение о транзакции {tx.hash}")

            await asyncio.sleep(10)
        except Exception as e:
            print(f"Ошибка в цикле мониторинга: {e}")
            await asyncio.sleep(10)


async def main():
    print("🚀 Запуск бота для отслеживания кошельков...")
    asyncio.create_task(monitor_wallets())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
