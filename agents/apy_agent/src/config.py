from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENSO_BASE_URL: str
    ENSO_API_KEY: str

    TELEGRAM_BOT_TOKEN_2: str


@lru_cache
def get_settings():
    return Settings()
