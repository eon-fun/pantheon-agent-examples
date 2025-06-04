import asyncio
from contextlib import asynccontextmanager

from base_agent.ray_entrypoint import BaseAgent
from config.config import config
from DB.sqlalchemy_database_manager import get_db, init_models
from fastapi import Depends, FastAPI
from loguru import logger
from ray import serve
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware
from tools.create_tweets_service import CreateTweetsService
from tools.get_tweets_service import TwitterCollectorClient
from twitter_echo_bot.DB.models.users_models import PGUser
from twitter_echo_bot.services.tracked_accounts_service import update_user_tracked_accounts_service
from twitter_echo_bot.services.user_service import create_user_service, get_user_service, update_user_service


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
                logger.error(f"Error when fetching tweets: {e}")

    async def create_tweets():
        while True:
            try:
                service = CreateTweetsService()
                await service.start()
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Error when fetching tweets: {e}")

    tasks = [asyncio.create_task(start_collecting_tweets()), asyncio.create_task(create_tweets())]

    await asyncio.gather(*tasks)


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("Application startup")
    await run_background_task()
    yield
    logger.info("Application shutdown")


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
        user_id = int(goal.split(".")[0])
        action = goal.split(".")[1]
        username = goal.split(".")[2]
        if action == "add_user":
            user_data = PGUser(id=user_id, username=username)
            return await create_user_service(user_data=user_data, db_session=session)
        if action == "update_user":
            persona_descriptor = goal.split(".")[3]
            prompt = goal.split(".")[4]
            user_data = PGUser(id=user_id, username=username, persona_descriptor=persona_descriptor, prompt=prompt)
            return await update_user_service(user_data=user_data, db_session=session)
        if action == "get_user":
            return await get_user_service(user_id=user_id, db_session=session)
        if action == "add_handles":
            handles = goal.split(".")[3:]
            return await update_user_tracked_accounts_service(
                user_id=user_id, twitter_handle=handles, db_session=session
            )


def get_agent(agent_args: dict):
    return FollowUnfollowBot.bind(**agent_args)


if __name__ == "__main__":
    serve.run(app, route_prefix="/")
