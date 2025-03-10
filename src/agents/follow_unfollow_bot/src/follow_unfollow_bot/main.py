import asyncio
from contextlib import asynccontextmanager
from typing import List
import datetime
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from DB.managers.user_manager import AlchemyUsersManager
from DB.sqlalchemy_database_manager import init_models, get_db
from config.config import config
from custom_logs.custom_logs import log
from routers.users_route import user_router
from tools.follow_for_like import process_follow_for_like
from ray import serve
from base_agent.ray_entrypoint import BaseAgent


async def background_task():
    """Фоновая задача, работающая бесконечно"""
    while True:
        log.info("Background task is running...")
        await process_follow_for_like()
        await asyncio.sleep(3600)


async def daily_task():
    while True:
        now = datetime.datetime.now()
        next_run = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Если уже после полуночи, берем следующее 00:00
        if now > next_run:
            next_run += datetime.timedelta(days=1)

        sleep_seconds = (next_run - now).total_seconds()
        log.info(f"Daily task will run in {sleep_seconds:.2f} seconds...")

        await asyncio.sleep(sleep_seconds)  # Ждем до 00:00
        log.info("Running daily task...")
        async for session in get_db():
            user_manager = AlchemyUsersManager(session)
            await user_manager.reset_followers_today()


@asynccontextmanager
async def lifespan(application: FastAPI):
    await init_models()
    task = asyncio.create_task(background_task())
    task2 = asyncio.create_task(daily_task())
    log.info("Application startup")

    yield
    task.cancel()
    task2.cancel()
    try:
        await task
        await task2
    except asyncio.CancelledError:
        log.info("Background task cancelled")
    log.info("Application shutdown")


ROUTERS: List[APIRouter] = [user_router]

app = FastAPI(
    lifespan=lifespan,
    title=config.APP_TITLE,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    docs_url=f"/{config.APP_DOCS_URL}/docs",
    redoc_url=f"/{config.APP_DOCS_URL}/redoc",
    openapi_url=f"/{config.APP_DOCS_URL}/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.FASTAPI.ALLOWED_ORIGINS,
    allow_credentials=config.FASTAPI.ALLOWED_CREDENTIALS,
    allow_methods=config.FASTAPI.ALLOWED_METHODS,
    allow_headers=config.FASTAPI.ALLOWED_HEADERS,
)


@serve.deployment
@serve.ingress(app)
class FollowUnfollowBot(BaseAgent):
    def __init__(self):
        for router in ROUTERS:
            app.include_router(router)

    @app.get("/")
    async def read_root(self):
        return {"message": f"Welcome to the {config.APP_TITLE} API!"}




app = FollowUnfollowBot.bind()

if __name__ == "__main__":
    serve.run(app, route_prefix="/")