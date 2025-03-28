from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

from solana_new_pairs.bot.message import build_message
from solana_new_pairs.config.config import config
from solana_new_pairs.service.collector_service import collect_full_data_about_coin

TOKEN = config.bot.bot_token

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message()
async def echo(message: types.Message):
    chat_id = message.chat.id
    coin_address = message.text
    data = await collect_full_data_about_coin(coin_address)
    message, img = await build_message(data)

    if img and len(message) < 1024:
        print("sending animation")
        print(len(message))
        await bot.send_animation(chat_id=chat_id, animation=img, caption=message, parse_mode="MARKDOWN",
                                 )
    else:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="MARKDOWN",
                               disable_web_page_preview=True)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("🛠 Available commands:\n/cex - get data from exchanges\n/dex get data from swap")


async def start_bot():
    await dp.start_polling(bot)
