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

    def get_protocols(self) -> List[Dict]:
        """Получает список поддерживаемых протоколов"""
        response = requests.get(f"{self.base_url}/protocols", headers=self.headers)
        return response.json()

    def get_defi_tokens(self, chain_id: int = 1, protocol_slug: Optional[str] = None) -> Dict:
        """Получает DeFi токены с их APY"""
        params = {
            "chainId": chain_id,
            "type": "defi"
        }
        if protocol_slug:
            params["protocolSlug"] = protocol_slug
        response = requests.get(f"{self.base_url}/tokens", headers=self.headers, params=params)
        return response.json()

    def is_valid_apy(self, apy) -> bool:
        """Проверяет, является ли APY допустимым значением"""
        if apy is None:
            return False
        try:
            apy_float = float(apy)
            return apy_float > 0 and apy_float < 1000
        except (TypeError, ValueError):
            return False

    async def find_best_pool(self, token_address: str, chain_id: int = 1) -> Dict:
        """Находит пул с лучшим APY для заданного токена"""
        print(f"\n🔍 Начинаю поиск пулов для токена: {token_address}")
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
                        print(f"✨ Найден подходящий пул в {protocol['slug']} с APY: {apy}%")

                        pool_info = {
                            "apy": apy if self.is_valid_apy(apy) else 0,
                            "protocol": protocol['slug'],
                            "protocol_name": protocol['name'],
                            "token_address": token["address"],
                            "primary_address": token.get("primaryAddress"),
                            "type": token.get("type")
                        }
                        best_pool["found_pools"].append(pool_info)

                        if self.is_valid_apy(apy) and apy > best_pool["apy"]:
                            best_pool.update({
                                "apy": apy,
                                "protocol": protocol['slug'],
                                "protocol_name": protocol['name'],
                                "token_address": token["address"],
                                "primary_address": token.get("primaryAddress"),
                                "type": token.get("type")
                            })

            except Exception as e:
                print(f"❌ Ошибка при обработке протокола {protocol['slug']}: {str(e)}")
                continue

        print(f"\n📈 Всего найдено пулов: {len(best_pool['found_pools'])}")
        if best_pool['protocol']:
            print(f"🏆 Лучший пул: {best_pool['protocol_name']} с APY {best_pool['apy']}%")

        return best_pool

    def format_investment_recommendation(self, best_pool: Dict) -> str:
        """Форматирует рекомендацию для отправки в Telegram"""
        if not best_pool["protocol"]:
            return "🔍 Не найдено подходящих пулов для инвестирования"

        # Сортируем пулы по APY
        sorted_pools = sorted(
            [pool for pool in best_pool["found_pools"] if self.is_valid_apy(pool["apy"])],
            key=lambda x: x["apy"],
            reverse=True
        )[:5]

        pools_text = "\n".join([
            f"• *{pool['protocol_name']}*: {pool['apy']:.2f}% APY"
            for pool in sorted_pools
        ])

        recommendation = f"""
🏆 *Лучшие варианты для инвестирования:*

{pools_text}

📊 *Подробности лучшего пула:*
• Протокол: `{best_pool['protocol_name']}`
• APY: `{best_pool['apy']:.2f}%`
• Тип: `{best_pool['type']}`
• Адрес токена: `{best_pool['token_address']}`
• Контракт: `{best_pool['primary_address']}`

💡 _Рекомендация: всегда проверяйте актуальность APY и условия протокола перед инвестированием._

#DeFi #Yield #Investment 🚀
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
