from contextlib import asynccontextmanager

from agent.ray_entrypoint import BaseAgent
from fastapi import FastAPI
from ray import serve


@asynccontextmanager
async def lifespan(app: FastAPI):
    # launch some tasks on app start
    yield
    # handle clean up

app = FastAPI(lifespan=lifespan)

@serve.deployment
class SubAgent:
    """This agent is a part of ray serve application, but it is not exposed for communication with the outside agents.
    We can use it to execute some tools or a custom logic to enable ray scaling capabilities.
    The `__call__` method in this class suggests that it could also just be a function instead.
    """

    def __call__(self, *args, **kwds):
        pass



@serve.deployment
@serve.ingress(app)
class ExampleAgent(BaseAgent):

    @app.post("/{goal}")
    def handle(self, goal: str, plan: dict | None = None):
        """This is one of the most important endpoint of MAS.
        It handles all requests made by handoff from other agents or by user."""
        pass



# serve run entrypoint:app
app = ExampleAgent.bind()


if __name__ == "__main__":
    serve.run(app, route_prefix="/")
