import asyncio
import datetime
from contextlib import asynccontextmanager

from agents_tools_logger.main import log
from base_agent.ray_entrypoint import BaseAgent
from fastapi import Depends, FastAPI
from follow_unfollow_bot.config.config import config
from follow_unfollow_bot.DB.managers.user_manager import AlchemyUsersManager
from follow_unfollow_bot.DB.sqlalchemy_database_manager import get_db, init_models
from follow_unfollow_bot.service.user_service import add_user_service, delete_user_service
from follow_unfollow_bot.tools.follow_for_like import process_follow_for_like
from ray import serve
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware


async def background_task():
    """Фоновая задача, работающая бесконечно"""
    while True:
        try:
            log.info("Background task is running...")
            await process_follow_for_like()
        except Exception as e:
            log.exception(f"Exception in background_task: {e}")
        await asyncio.sleep(3600)


async def daily_task():
    while True:
        try:
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
        except Exception as e:
            log.exception(f"Exception in daily_task: {e}")
            await asyncio.sleep(10)  # Задержка перед повторной попыткой в случае ошибки


@asynccontextmanager
async def lifespan(application: FastAPI):
    await init_models()

    # Запуск фоновых задач
    tasks = [asyncio.create_task(background_task()), asyncio.create_task(daily_task())]
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        log.info("Background tasks cancelled")
    log.info("Application startup")

    yield
    log.info("Application shutdown")


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
class FollowUnfollowBot(BaseAgent):
    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None, session: AsyncSession = Depends(get_db)):
        twitter_id = int(goal.split(".")[0])
        action = goal.split(".")[1]
        if action.lower() == "add":
            await add_user_service(session, twitter_id)
        elif action.lower() == "delete":
            await delete_user_service(session, twitter_id)


app = FollowUnfollowBot.bind()

if __name__ == "__main__":
    serve.run(app, route_prefix="/")
