import asyncio
import json

from aiogram.enums import ParseMode

from solana_new_pairs.DB.manager.coin_manager import AlchemyBaseCoinManager
from solana_new_pairs.DB.sqlalchemy_database_manager import get_db
from solana_new_pairs.bot.bot import bot
from solana_new_pairs.bot.message import build_message
from solana_new_pairs.service.collector_service import collect_full_data_about_coin


def escape_markdown_v2(text):
    """Экранирует специальные символы для MarkdownV2"""
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)


def split_text(text, max_length=4000):
    """Функция для разбиения длинного текста на части"""
    parts = []
    while text:
        parts.append(text[:max_length])
        text = text[max_length:]
    return parts


async def post_new_coins_in_bot():
    """Постит новые монеты в бот"""
    async for session in get_db():
        coin_manager = AlchemyBaseCoinManager(session)
        new_coins = await coin_manager.mark_unposted_as_posted()
        for coin in new_coins:
            print(f"Постим новую монету с адресом {coin.token_address}")
            data = await collect_full_data_about_coin(coin.token_address)
            message, img = await build_message(data)
            if img and len(message) < 1024:
                print("sending animation")
                print(len(message))
                await bot.send_animation(chat_id=-4777229652, animation=img, caption=message, parse_mode="MARKDOWN")
            else:
                await bot.send_message(chat_id=-4777229652, text=message, parse_mode="MARKDOWN",
                               disable_web_page_preview=True)

