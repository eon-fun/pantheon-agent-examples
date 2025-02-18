from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import Command

from infrastructure.configs.config import get_settings
from simple_ai_agents.ai_apy_agent_ray_deployment.entrypoint import agent

settings = get_settings()


bot = Bot(token=settings.TELEGRAM_BOT_TOKEN_2)
dp = Dispatcher()


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