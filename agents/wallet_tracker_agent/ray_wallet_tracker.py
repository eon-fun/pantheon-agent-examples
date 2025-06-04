import os
from dataclasses import dataclass

import aiohttp
import ray
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
    """Конвертация hex значения в decimal"""
    if not hex_string.startswith("0x"):
        return float(hex_string)
    try:
        dec_value = int(hex_string, 16)
        if base_type == "value":
            return float(dec_value)
        return dec_value  # для timestamp возвращаем int
    except ValueError:
        return 0.0


@ray.remote
class WalletTrackingAgent:
    def __init__(self):
        # Initialize constants
        self.WATCHED_WALLETS_KEY = "watched_wallets"
        self.PROCESSED_TXS_KEY = "processed_transactions"
        self.ANKR_API_KEY = os.getenv("ANKR_API_KEY")
        self.ANKR_API_URL = f"https://rpc.ankr.com/multichain/{self.ANKR_API_KEY}" if self.ANKR_API_KEY else None

        # Initialize Redis
        self.db = RedisDB()
        print("✅ WalletTrackingAgent initialized")

    async def check_wallet_transactions(self, wallet_address: str) -> list[Transaction]:
        """Получение транзакций через Ankr RPC API"""
        processed_txs = set(self.db.get_set(f"{self.PROCESSED_TXS_KEY}:{wallet_address}"))
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
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ANKR_API_URL, headers=headers, json=payload, timeout=30) as response:
                    if response.status != 200:
                        print(f"Ошибка API статус {response.status}")
                        return []

                    data = await response.json()
                    if "error" in data:
                        print(f"Ошибка API: {data['error']}")
                        return []

                    transactions_data = data.get("result", {}).get("transactions", [])
                    print(f"Получено {len(transactions_data)} транзакций")

                    for tx in transactions_data:
                        tx_hash = tx.get("hash")
                        if tx_hash in processed_txs:
                            continue

                        try:
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
                        except Exception as e:
                            print(f"Ошибка при обработке транзакции {tx}: {e}")

        except Exception as e:
            print(f"Ошибка при получении транзакций для {wallet_address}: {e}")

        return transactions

    def format_transaction_message(self, tx: Transaction) -> str:
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

    async def add_wallet(self, wallet: str) -> bool:
        """Adds a wallet to the watched list."""
        try:
            if len(wallet) != 42 or not wallet.startswith("0x"):
                return False
            self.db.add_to_set(self.WATCHED_WALLETS_KEY, wallet)
            return True
        except Exception as e:
            print(f"❌ Error adding wallet {wallet}: {e}")
            return False

    async def remove_wallet(self, wallet: str) -> bool:
        """Removes a wallet from the watched list."""
        try:
            self.db.r.srem(self.WATCHED_WALLETS_KEY, wallet)
            return True
        except Exception as e:
            print(f"❌ Error removing wallet {wallet}: {e}")
            return False

    async def get_wallet_list(self) -> set:
        """Returns the list of watched wallets."""
        return self.db.get_set(self.WATCHED_WALLETS_KEY)

    async def process_wallets(self) -> list[dict]:
        """Main method to process wallets and check for new transactions."""
        try:
            wallets = await self.get_wallet_list()
            if not wallets:
                return []

            all_messages = []
            for wallet in wallets:
                transactions = await self.check_wallet_transactions(wallet)
                for tx in transactions:
                    message = self.format_transaction_message(tx)
                    all_messages.append({"message": message, "tx_hash": tx.hash, "wallet": wallet})
                    self.db.add_to_set(f"{self.PROCESSED_TXS_KEY}:{wallet}", tx.hash)

            return all_messages
        except Exception as e:
            print(f"❌ Error in process_wallets: {e}")
            return []
