import asyncio
import json

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command

from solana_new_pairs.bot.message import build_message
from solana_new_pairs.service.collector_service import collect_full_data_about_coin

TOKEN = "5343231561:AAGHqNDPaW0AWFu1G86_d4SzklK6aZVzxPM"

bot = Bot(token=TOKEN)
dp = Dispatcher()


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


@dp.message()
async def echo(message: types.Message):
    coin_address = message.text
    data = await collect_full_data_about_coin(coin_address)
    message , img = await build_message(data)

    if img and len(message) < 1024:
        print("sending animation")
        print(len(message))
        await bot.send_animation(chat_id=-4777229652, animation=img, caption=message, parse_mode="MARKDOWN",
                                 )
    else:
        await bot.send_message(chat_id=-4777229652, text=message, parse_mode="MARKDOWN",
                               disable_web_page_preview=True)
    # json_data = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    # parts = split_text(json_data)
    # for part in parts:
    #     escaped_part = escape_markdown_v2(part)
    #     await message.answer(f"```json\n{escaped_part}\n```", parse_mode="MarkdownV2")
    #     await asyncio.sleep(2)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("🛠 Available commands:\n/cex - get data from exchanges\n/dex get data from swap")


async def start_bot():
    await dp.start_polling(bot)
