import time

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
import json
import requests
from typing import Dict, List, Optional

TELEGRAM_BOT_TOKEN = "7633131821:AAForOPCLS045IFHihMf49UozGwKL7IMbpU"
ENSO_API_KEY = "1e02632d-6feb-4a75-a157-documentation"


class APYAgent:
    def __init__(self, api_key: str):
        self.base_url = "https://api.enso.finance/api/v1"
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def get_token_price(self, token_address: str, chain_id: int = 1) -> Dict:
        """Получает информацию о цене токена"""
        url = f"{self.base_url}/prices/{chain_id}/{token_address}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def is_token_active(self, token_address: str, chain_id: int = 1) -> bool:
        """Проверяет активность токена по данным о цене"""
        price_data = self.get_token_price(token_address, chain_id)
        if not price_data:
            print("⚠️ Не удалось получить данные о цене")
            return False

        price = price_data.get("price")
        if not price or float(price) == 0:
            print("⚠️ Токен не имеет актуальной цены")
            return False

        timestamp = price_data.get("timestamp")
        if timestamp:
            current_time = int(time.time())
            if current_time - int(timestamp) > 86400:
                print("⚠️ Данные о цене устарели")
                return False

        print(f"✅ Токен активен:")
        print(f"   - Цена: ${float(price):,.2f}")
        print(f"   - Название: {price_data.get('name')}")
        print(f"   - Символ: {price_data.get('symbol')}")
        return True

    def get_protocols(self) -> List[Dict]:
        """Получает список поддерживаемых протоколов"""
        response = requests.get(f"{self.base_url}/protocols", headers=self.headers)
        return response.json()

    def get_defi_tokens(self, chain_id: int = 1, protocol_slug: Optional[str] = None) -> Dict:
        """Получает DeFi токены с их APY и дополнительной информацией"""
        params = {
            "chainId": chain_id,
            "type": "defi",
            "includeMetrics": "true"
        }
        if protocol_slug:
            params["protocolSlug"] = protocol_slug

        response = requests.get(f"{self.base_url}/tokens", headers=self.headers, params=params)
        return response.json()

    def is_valid_pool(self, token: Dict, apy: float) -> bool:
        """Проверяет, является ли пул надежным и безопасным для инвестирования"""
        print("\n🔍 Проверка безопасности пула:")

        if not apy:
            print(f"⚠️ Отсутствует APY")
            return False

        if apy > 100:
            print(f"⚠️ Подозрительно высокий APY: {apy}%")
            return False

        if apy < 0.1:
            print(f"⚠️ Слишком низкий APY: {apy}%")
            return False

        underlying_tokens = token.get("underlyingTokens", [])
        if len(underlying_tokens) < 2:
            print("⚠️ Недостаточно базовых токенов для пула")
            return False

        for underlying_token in underlying_tokens:
            token_address = underlying_token["address"]
            if not self.is_token_active(token_address, token["chainId"]):
                print(f"⚠️ Базовый токен {token_address} неактивен")
                return False

        required_fields = ["chainId", "address", "decimals", "type", "protocolSlug"]
        missing_fields = [field for field in required_fields if field not in token]
        if missing_fields:
            print(f"⚠️ Отсутствуют обязательные поля: {', '.join(missing_fields)}")
            return False

        print(f"✅ Пул прошел проверку безопасности:")
        print(f"   - Протокол: {token['protocolSlug']}")
        print(f"   - APY: {apy}%")
        print(f"   - Тип: {token['type']}")
        print(f"   - Основной контракт: {token.get('primaryAddress')}")
        print(f"   - Количество базовых токенов: {len(underlying_tokens)}")
        return True

    async def find_best_pool(self, token_address: str, chain_id: int = 1) -> Dict:
        """Находит пул с лучшим APY для заданного токена"""
        print(f"\n🔍 Начинаю поиск безопасных пулов для токена: {token_address}")
        protocols = self.get_protocols()
        print(f"📋 Получено протоколов: {len(protocols)}")

        best_pool = {
            "apy": 0,
            "protocol": None,
            "token_address": None,
            "found_pools": []
        }

        for protocol in protocols:
            try:
                print(f"\n🔄 Проверяю протокол: {protocol['name']} ({protocol['slug']})")

                if not any(chain['id'] == chain_id for chain in protocol['chains']):
                    print(f"⏩ Пропускаю {protocol['slug']} - сеть {chain_id} не поддерживается")
                    continue

                defi_tokens = self.get_defi_tokens(chain_id, protocol['slug'])
                tokens = defi_tokens.get("data", [])
                print(f"📊 Найдено {len(tokens)} токенов в {protocol['slug']}")

                for token in tokens:
                    underlying_addresses = [t['address'].lower() for t in token.get('underlyingTokens', [])]
                    if token_address.lower() in underlying_addresses:
                        apy = token.get("apy")
                        print(f"\n🔎 Найден пул в {protocol['slug']} с параметрами:")
                        print(f"- APY: {apy}%")
                        print(f"- Raw token data: {json.dumps(token, indent=2)}")

                        if not self.is_valid_pool(token, apy):
                            continue

                        pool_info = {
                            "apy": apy,
                            "protocol": protocol['slug'],
                            "protocol_name": protocol['name'],
                            "token_address": token["address"],
                            "primary_address": token.get("primaryAddress"),
                            "type": token.get("type"),
                            "tvl": token.get("tvl"),
                            "days_old": token.get("daysOld"),
                            "transaction_count": token.get("transactionCount")
                        }
                        best_pool["found_pools"].append(pool_info)

                        if apy > best_pool["apy"]:
                            best_pool.update(pool_info)

            except Exception as e:
                print(f"❌ Ошибка при обработке протокола {protocol['slug']}: {str(e)}")
                continue

        print(f"\n📈 Всего найдено безопасных пулов: {len(best_pool['found_pools'])}")
        if best_pool['protocol']:
            print(f"🏆 Лучший пул: {best_pool['protocol_name']} с APY {best_pool['apy']}%")

        return best_pool

    def format_investment_recommendation(self, best_pool: Dict) -> str:
        """Форматирует рекомендацию для отправки в Telegram"""
        if not best_pool["protocol"]:
            return "🔍 Не найдено подходящих пулов для инвестирования"

        sorted_pools = sorted(
            [pool for pool in best_pool["found_pools"]],
            key=lambda x: x["apy"],
            reverse=True
        )[:5]

        token_prices = {}
        for token in best_pool.get("underlyingTokens", []):
            price_data = self.get_token_price(token["address"], best_pool["chainId"])
            if price_data:
                token_prices[token["address"]] = {
                    "price": float(price_data.get("price", 0)),
                    "symbol": price_data.get("symbol", "Unknown")
                }

        tokens_info = "\n".join([
            f"    - {data['symbol']}: ${data['price']:,.2f}"
            for addr, data in token_prices.items()
        ])

        pools_text = "\n".join([
            f"• *{pool['protocol_name']}*:\n"
            f"  - APY: {pool['apy']:.2f}%\n"
            f"  - Тип пула: {pool['type']}\n"
            f"  - Контракт: `{pool['primary_address']}`"
            for pool in sorted_pools
        ])

        recommendation = f"""
🏆 *Найденные пулы для инвестирования:*

{pools_text}

📊 *Подробности лучшего пула:*
• Протокол: `{best_pool['protocol_name']}`
• APY: `{best_pool['apy']:.2f}%`
• Тип: `{best_pool['type']}`
• Адрес пула: `{best_pool['token_address']}`
• Контракт: `{best_pool['primary_address']}`

💰 *Токены в пуле:*
{tokens_info}

💡 _Условия безопасности:_
• Реалистичный APY (0.1% - 100%)
• Все токены имеют актуальную цену
• Активный торговый объем
• Регулярное обновление це
"""
        return recommendation


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
agent = APYAgent(ENSO_API_KEY)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = """
👋 Привет! Я помогу найти лучший пул для инвестирования твоих токенов.

*Доступные команды:*
• /find_pools <адрес_токена> - найти лучшие пулы для токена
• /help - показать это сообщение

*Пример использования:*
`/find_pools 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`
"""
    await message.answer(welcome_text, parse_mode="Markdown")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await cmd_start(message)


@dp.message(Command("find_pools"))
async def find_pools(message: Message):
    print(f"\n🤖 Получена команда поиска пулов от пользователя {message.from_user.username}")
    try:
        token_address = message.text.split()[1]
        print(f"📝 Получен адрес токена: {token_address}")
    except IndexError:
        print("⚠️ Пользователь не указал адрес токена")
        await message.answer(
            "⚠️ Пожалуйста, укажите адрес токена.\nПример: `/find_pools 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`",
            parse_mode="Markdown")
        return
    status_message = await message.answer("🔍 Ищу лучшие пулы для инвестирования...")

    try:
        best_pool = await agent.find_best_pool(token_address)

        recommendation = agent.format_investment_recommendation(best_pool)
        await status_message.edit_text(recommendation, parse_mode="Markdown")

    except Exception as e:
        error_message = f"❌ Произошла ошибка при поиске пулов: {str(e)}"
        await status_message.edit_text(error_message)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
