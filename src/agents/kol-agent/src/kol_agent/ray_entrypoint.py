from contextlib import asynccontextmanager

from base_agent.ray_entrypoint import BaseAgent
from fastapi import FastAPI
from ray import serve
from langfuse.callback import CallbackHandler
from pydantic import BaseModel, Field

from kol_agent.raid import get_raid_workflow
from kol_agent.config import get_config


from twitter_ambassador_utils.main import set_like, TwitterAuthClient
from tweetscout_utils.main import search_tweets
from redis_client.main import get_redis_db
import logging
import time
import random

logger = logging.getLogger(__name__)

config = get_config()

class InputModel(BaseModel):
    target_tweet_id: str = Field(..., description="The ID of the tweet to raid", example="1719810222222222222")
    bot_count: int = Field(..., description="The number of bots to use", example=10)
    raid_minutes: float = Field(..., description="The number of minutes to raid", example=0.1)

class OutputModel(BaseModel):
    success: bool
    message: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # launch some tasks on app start
    yield
    # handle clean up

app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class KolAgent(BaseAgent):
    def __init__(self):
        langfuse_handler = CallbackHandler(
            public_key = config.LANGFUSE_PUBLIC_KEY,
            secret_key = config.LANGFUSE_SECRET_KEY,
            host = config.LANGFUSE_HOST,
            trace_name="kol-agent"
        )
        workflow = get_raid_workflow()
        self.graph = workflow.compile().with_config({"callbacks": [langfuse_handler]})

    @app.post("/{goal}")
    async def handle(self, goal: str, input: InputModel, plan: dict | None = None):
        state = {
            "target_tweet_id": input.target_tweet_id,
            "bot_count": input.bot_count,
            "raid_minutes": input.raid_minutes,
        }
        await self.graph.ainvoke(state)
        return OutputModel(success=True, message="Raid started")

    @app.get("/all_accounts")
    async def all_accounts(self):
        db = get_redis_db()
        return {"accounts": db.get_twitter_data_keys()}
    
    @app.get("/all_keys_redis")
    async def all_keys_redis(self):
        db = get_redis_db()
        return {"keys": db.r.keys()}
    
    @app.post("/set_likes")
    async def set_likes(self, input: InputModel):
        db = get_redis_db()
        accounts = db.get_active_twitter_accounts()
        for account in accounts:
            time.sleep(random.randint(30, 90))
            account_access_token = await TwitterAuthClient.get_access_token(account)
            result = await set_like(
                token=account_access_token,
                tweet_id=input.target_tweet_id,
                user_id=TwitterAuthClient.get_static_data(account)['id'],
            )
            if result.get('data', {}).get('liked'):
                logger.warning(f'Liked tweet: {account=} {input.target_tweet_id=}')
                db.add_to_set(f'user_likes:{account}', input.target_tweet_id)
            else:
                logger.error(f'Failed to like tweet: {account=} {input.target_tweet_id=}')
        return {"success": True}


def get_agent(agent_args: dict):
    return KolAgent.bind(**agent_args)

if __name__ == "__main__":
    serve.run(app, route_prefix="/")