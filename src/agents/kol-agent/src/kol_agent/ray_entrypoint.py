from contextlib import asynccontextmanager

from base_agent.ray_entrypoint import BaseAgent
from fastapi import FastAPI
from fastapi import BackgroundTasks
from ray import serve
from langfuse.callback import CallbackHandler
from pydantic import BaseModel, Field

from kol_agent.raid import get_raid_workflow
from kol_agent.config import get_config

from twitter_ambassador_utils.main import TwitterAuthClient
from kol_agent.models.raid_state import BotsModel
from redis_client.main import get_redis_db
import logging
import time
import random
from typing import List


logger = logging.getLogger(__name__)

config = get_config()

class InputModel(BaseModel):
    target_tweet_id: str = Field(..., description="The ID of the tweet to raid", example="1719810222222222222")
    tweet_text: str = Field(..., description="The text of the tweet to raid", example="")
    bot_accounts: List[BotsModel] = Field(..., 
                                          description="The accounts of the bots to use", 
                                          example=[
                                            {
                                                "username": "elonmusk", 
                                                "role": "advocate", 
                                                "account_access_token": "1234567890", 
                                                "user_id": "1234567890"
                                            }])
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

    async def handle_raid(self, state: dict):
        await self.graph.ainvoke(state)

    @app.post("/{goal}")
    async def handle(self, goal: str, input: InputModel, background_tasks: BackgroundTasks, plan: dict | None = None):
        state = {
            "target_tweet_id": input.target_tweet_id,
            "bot_accounts": input.bot_accounts,
            "raid_minutes": input.raid_minutes,
            "tweet_content": input.tweet_text,
        }
        background_tasks.add_task(self.handle_raid, state)
        return OutputModel(success=True, message="Raid started")

    @app.get("/all_accounts")
    async def all_accounts(self):
        db = get_redis_db()
        accounts = db.get_active_twitter_accounts()
        accounts_data = []
        excepted_errors = []
        for account in accounts:
            account_access_token = None
            user_id = None
            print(f'Getting data for account: {account=}')
            try:
                account_access_token = await TwitterAuthClient.get_access_token(account)
            except Exception as token_error:
                print(f'Failed to get access token for account: {account=} {token_error=}')
                excepted_errors.append(f"Token error for {account}: {str(token_error)}")
            else:
                print(f'Successfully got access token for account: {account=}, {account_access_token=}')
            
            try:
                user_id = TwitterAuthClient.get_static_data(account)['id']
            except Exception as user_id_error:
                print(f'Failed to get user id for account: {account=} {user_id_error=}')
                excepted_errors.append(f"User id error for {account}: {str(user_id_error)}")
            else:
                print(f'Successfully got user id for account: {account=}, {user_id=}')
            
            accounts_data.append({
                "account": account,
                "user_id": user_id,
                "access_token": account_access_token,
            })

        return {"accounts": accounts_data, "excepted_errors": excepted_errors}


def get_agent(agent_args: dict):
    return KolAgent.bind(**agent_args)

if __name__ == "__main__":
    serve.run(app, route_prefix="/")
