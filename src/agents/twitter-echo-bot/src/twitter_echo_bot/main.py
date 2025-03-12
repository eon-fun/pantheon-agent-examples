import asyncio
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware
from base_agent.ray_entrypoint import BaseAgent

from routers.tracked_accounts import tracked_accounts_router
from routers.user import user_router
from config.config import config


from DB.sqlalchemy_database_manager import init_models, get_db
from ray import serve
from agents_tools_logger.main import log
from tools.create_tweets_service import CreateTweetsService
from tools.get_tweets_service import TwitterCollectorClient


async def init_app():
    await init_models()


async def run_background_task():
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

@asynccontextmanager
async def lifespan(application: FastAPI):
    log.info("Application startup")
    await run_background_task()
    yield
    log.info("Application shutdown")


ROUTERS: List[APIRouter] = [user_router,
                            tracked_accounts_router]


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
for router in ROUTERS:
    app.include_router(router)



@serve.deployment
@serve.ingress(app)
class FollowUnfollowBot(BaseAgent):
    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None,
                     session: AsyncSession = Depends(get_db)):
        pass

if __name__ == "__main__":
    serve.run(app, route_prefix="/")