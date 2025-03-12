import asyncio

from DB.sqlalchemy_database_manager import init_models

from custom_logs.custom_logs import log
from tools.create_tweets_service import CreateTweetsService
from tools.get_tweets_service import TwitterCollectorClient


async def init_app():
    await init_models()


async def main():
    await init_app()

    async def start_collecting_tweets():
        while True:
            try:
                client = TwitterCollectorClient()
                await client.start_parsing_tweets()
                await asyncio.sleep(500)
            except Exception as e:
                log.error(f"Ошибка при сборе твитов: {e}")

    async def create_tweets():
        while True:
            try:
                service = CreateTweetsService()
                await service.start()
                await asyncio.sleep(5)
            except Exception as e:
                log.error(f"Ошибка при создании твитов: {e}")

    tasks = [
        asyncio.create_task(start_collecting_tweets()),
        asyncio.create_task(create_tweets())
    ]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Программа остановлена вручную.")
