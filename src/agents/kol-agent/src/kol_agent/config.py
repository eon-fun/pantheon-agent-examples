from pydantic_settings import BaseSettings
from functools import lru_cache


class Config(BaseSettings):
    LIKE_PERCENTAGE: float = 0.9
    COMMENT_PERCENTAGE: float = 0.4
    REPLY_PERCENTAGE: float = 0.6
    RETWEET_PERCENTAGE: float = 0.5

    LANGFUSE_SECRET_KEY: str = "sk-lf-03687f3f-9cc8-4661-b1a4-acf432360552"
    LANGFUSE_PUBLIC_KEY: str = "pk-lf-61839399-0194-403e-9d21-6e7dcd3f5041"
    LANGFUSE_HOST: str = "https://langfuse.dev.pntheon.ai"


@lru_cache
def get_config() -> Config:
    return Config()
