from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl
from functools import lru_cache
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    creativity_base_url: HttpUrl = Field(default=HttpUrl('https://api.creativity.ai/v1'))
    creativity_api_id: str = Field(...)
    creativity_api_key: str = Field(...)

    deployment_name: str = Field(default="CreativityService")
    num_replicas: int = Field(default=1, ge=1)

    log_level: str = Field(default="INFO")


@lru_cache()
def get_settings() -> Settings:
    try:
        settings = Settings()
        return settings
    except Exception as e:
        raise
