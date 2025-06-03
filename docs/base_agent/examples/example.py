from base_agent import BaseAgent
from base_agent.config import BasicAgentConfig
from ray.serve.deployment import Application


class CustomAgent(BaseAgent):
    async def handle(self, goal: str, plan: dict | None = None, context: Any = None):
        if goal == "special_task":
            return await self.handle_special_task(context)
        return await super().handle(goal, plan, context)

    async def handle_special_task(self, context):
        # Custom implementation
        return {"status": "success"}


def agent_builder(args: dict) -> Application:
    return CustomAgent.bind(config=BasicAgentConfig(**args))
