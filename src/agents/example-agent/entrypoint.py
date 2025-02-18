from contextlib import asynccontextmanager
from urllib.parse import urljoin

import requests
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
class ExampleAgent:
    """This is a core agent and entrypoint to this multi agent system.
    It's recommended to spin only one agent for each ray serve application.
    The reason is that implementation of multi agent system on this level does not allow us
    to use a communication between agents in swarm mode.
    Possible use cases - we can implement a team of agents on this level like a CrewAI did.
    In this case the agent should control a flow as orchestrator and validate execution logic of team by itself.
    """
    def __init__(self, *args, **kwargs):
        """Initializes agent with some params passed to `bind` method"""
        pass

    @app.post("/{goal}")
    def handle(self, goal: str, plan: dict | None = None):
        """This is one of the most important endpoint of MAS.
        It handles all requests made by handoff from other agents or by user."""
        pass

    def handoff(self, endpoint: str, goal: str, plan: dict):
        """This method means that agent can't find a solution (wrong route/wrong plan/etc)
        and decide to handoff the task to another agent. """
        return requests.post(urljoin(endpoint, goal), json=plan).json()



# serve run entrypoint:app
app = ExampleAgent.bind()


if __name__ == "__main__":
    serve.run(app, route_prefix="/")
