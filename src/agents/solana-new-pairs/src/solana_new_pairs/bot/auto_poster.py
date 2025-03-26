import asyncio
from solana_new_pairs.DB.manager.coin_manager import AlchemyBaseCoinManager
from solana_new_pairs.DB.sqlalchemy_database_manager import get_db
from solana_new_pairs.bot.bot import bot
from solana_new_pairs.bot.message import build_message
from solana_new_pairs.service.collector_service import collect_full_data_about_coin

message_queue = asyncio.Queue()
SEND_DELAY = 1


async def message_worker():
    """ Воркер, который отправляет сообщения из очереди с задержкой """
    while True:
        chat_id, message, img = await message_queue.get()  # Ждем сообщение из очереди

        try:
            if img and len(message) < 1024:
                await bot.send_photo(chat_id=chat_id, photo=img, caption=message, parse_mode="MARKDOWN")
            else:
                await bot.send_message(chat_id=chat_id, text=message, parse_mode="MARKDOWN",
                                       disable_web_page_preview=True)

            # print(f"Отправлено: {message}")
        except Exception as e:
            print(f"Ошибка при отправке: {e}")
        finally:
            message_queue.task_done()  # Сообщаем, что обработали элемент
            await asyncio.sleep(SEND_DELAY)  # Задержка перед отправкой следующего


async def add_message_to_queue(message: str, img: str = None):
    """ Добавляет сообщение в очередь """
    await message_queue.put((-4777229652, message, img))


async def post_new_coins_in_bot():
    """Постит новые монеты в бот"""
    async for session in get_db():
        coin_manager = AlchemyBaseCoinManager(session)
        new_coins = await coin_manager.mark_unposted_as_posted()
        for coin in new_coins:
            print(f"Постим новую монету с адресом {coin.token_address}")
            data = await collect_full_data_about_coin(coin.token_address)
            await asyncio.sleep(1)
            message, img = await build_message(data)
            await add_message_to_queue(message, img)