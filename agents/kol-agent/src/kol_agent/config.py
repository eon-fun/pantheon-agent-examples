from functools import lru_cache

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    LIKE_PERCENTAGE: float = 0.9
    COMMENT_PERCENTAGE: float = 0.6
    REPLY_PERCENTAGE: float = 0.6
    RETWEET_PERCENTAGE: float = 0.6

    LANGFUSE_SECRET_KEY: str
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_HOST: str


@lru_cache
def get_config() -> Config:
    return Config()
