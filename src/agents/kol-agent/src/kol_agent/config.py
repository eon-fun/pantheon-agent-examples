from pydantic_settings import BaseSettings
from functools import lru_cache


class Config(BaseSettings):
    LIKE_PERCENTAGE: float = 0.9
    COMMENT_PERCENTAGE: float = 0.4
    REPLY_PERCENTAGE: float = 0.6
    RETWEET_PERCENTAGE: float = 0.5

    LANGFUSE_SECRET_KEY: str
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_HOST: str


@lru_cache
def get_config() -> Config:
    return Config()