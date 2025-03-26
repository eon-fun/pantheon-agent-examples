import asyncio

from solana_new_pairs.DB.sqlalchemy_database_manager import init_models
from solana_new_pairs.bot.auto_poster import post_new_coins_in_bot, message_worker
from solana_new_pairs.bot.bot import start_bot
from solana_new_pairs.service.dextools_service import DextoolsAPIWrapper, collect_and_store_data


async def main():
    await init_models()
    dex_tools_api = DextoolsAPIWrapper(api_key="Kv7BZ8mwvU4vFoaaS8eEJ3UvmXG4x7Qk71uLesRF", plan="trial")

    async def start_collecting_data_from_dextools(dex_tools_api: DextoolsAPIWrapper):

        while True:
            try:
                await collect_and_store_data(dex_tools_api)  # Твой код обновления

            except Exception as e:
                print(e)

            await asyncio.sleep(10)

    async def post_new_coins():
        while True:
            try:
                await post_new_coins_in_bot()

            except Exception as e:
                print(e)

            await asyncio.sleep(1)

    async def bot_task():

        await start_bot()

    tasks = [
        asyncio.create_task(bot_task()),
        asyncio.create_task(start_collecting_data_from_dextools(dex_tools_api)),
        asyncio.create_task(post_new_coins()),
        asyncio.create_task(message_worker())
    ]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа остановлена вручную.")
