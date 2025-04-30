from contextlib import asynccontextmanager

from base_agent.ray_entrypoint import BaseAgent
from fastapi import FastAPI
from ray import serve
from langfuse.callback import CallbackHandler
from pydantic import BaseModel, Field

from kol_agent.raid import get_raid_workflow
from kol_agent.config import get_config


config = get_config()

class InputModel(BaseModel):
    target_tweet_id: str = Field(..., description="The ID of the tweet to raid", example="1719810222222222222")
    bot_count: int = Field(..., description="The number of bots to use", example=10)
    raid_minutes: float = Field(..., description="The number of minutes to raid", example=0.1)

    public_key: str = Field(..., description="The public key of the Langfuse project", example="1234567890")
    secret_key: str = Field(..., description="The secret key of the Langfuse project", example="1234567890")
    host: str = Field(..., description="The host of the Langfuse project", example="https://langfuse.dev.pntheon.ai")


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
        workflow = get_raid_workflow()
        self.graph = workflow.compile()

    @app.post("/{goal}")
    async def handle(self, goal: str, input: InputModel, plan: dict | None = None):
        langfuse_handler = CallbackHandler(
            public_key = input.public_key,
            secret_key = input.secret_key,
            host = input.host,
        )
        state = {
            "target_tweet_id": input.target_tweet_id,
            "bot_count": input.bot_count,
            "raid_minutes": input.raid_minutes,
        }
        data = await self.graph.ainvoke(state, callbacks=[langfuse_handler])
        return OutputModel(success=True, message=str(data))



def get_agent(agent_args: dict):
    return KolAgent.bind(**agent_args)

if __name__ == "__main__":
    serve.run(app, route_prefix="/")