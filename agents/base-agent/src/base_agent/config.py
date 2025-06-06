import json
from functools import lru_cache

from pydantic_settings import BaseSettings


class BasicAgentConfig(BaseSettings):
    system_prompt: str = "Act as a helpful assistant. You are given a task to complete."

    agents: dict[str, str] = {}

    def __str__(self) -> str:
        """Serialize the config to a pretty JSON string for prompt usage."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)


@lru_cache
def get_agent_config() -> BasicAgentConfig:
    return BasicAgentConfig()
