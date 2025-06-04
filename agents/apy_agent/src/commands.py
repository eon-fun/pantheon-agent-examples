from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from .config import get_settings

bot = Bot(token=get_settings().TELEGRAM_BOT_TOKEN_2)
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
    pass
