from functools import lru_cache

from base_agent.orchestration.models import WorkflowSettings
from pydantic_settings import BaseSettings


class BasicWorkflowConfig(BaseSettings):
    WORKFLOWS_TO_RUN: dict[str, WorkflowSettings] = {}
    WORKFLOW_STEP_MAX_RETRIES: int = 5  # Задаю дефолт так как мне кажется, что она не настолько динамическая


@lru_cache
def get_workflow_config() -> BasicWorkflowConfig:
    return BasicWorkflowConfig()
