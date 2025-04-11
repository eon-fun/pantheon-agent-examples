import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from ray import serve

from solana_new_pairs.DB.sqlalchemy_database_manager import init_models
from solana_new_pairs.bot.auto_poster import post_new_coins_in_bot, message_worker
from solana_new_pairs.bot.bot import start_bot
from solana_new_pairs.config.config import config
from solana_new_pairs.service.dextools_service import DextoolsAPIWrapper, collect_and_store_data
from base_agent.ray_entrypoint import BaseAgent


async def main():
    await init_models()
    dex_tools_api = DextoolsAPIWrapper(api_key=config.dex_tools.api_key, plan=config.dex_tools.plan)

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


@asynccontextmanager
async def lifespan(application: FastAPI):
    await main()
    yield


app = FastAPI(
    lifespan=lifespan,
    title=config.app_title,
    description=config.app_description,
    version=config.app_version,
    docs_url=f"/{config.app_docs_url}/docs",
    redoc_url=f"/{config.app_docs_url}/redoc",
    openapi_url=f"/{config.app_docs_url}/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.fastapi.allowed_origins,
    allow_credentials=config.fastapi.allowed_credentials,
    allow_methods=config.fastapi.allowed_methods,
    allow_headers=config.fastapi.allowed_headers,
)


@serve.deployment
@serve.ingress(app)
class SolanaNewPairsBot(BaseAgent):
    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None):
        return {"status": "main запущен"}


app = SolanaNewPairsBot.bind()
if __name__ == "__main__":
    serve.run(app, route_prefix="/")
