from contextlib import asynccontextmanager

from base_agent.ray_entrypoint import BaseAgent
from fastapi import FastAPI
from ray import serve
from langfuse.callback import CallbackHandler
from pydantic import BaseModel

from kol_agent.raid import get_raid_workflow


class InputModel(BaseModel):
    target_tweet_id: str
    bot_count: int
    raid_minutes: float


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
        langfuse_handler = CallbackHandler()
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



def get_agent(agent_args: dict):
    return KolAgent.bind(**agent_args)

if __name__ == "__main__":
    serve.run(app, route_prefix="/")