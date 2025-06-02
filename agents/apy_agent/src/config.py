from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    ENSO_BASE_URL: str
    ENSO_API_KEY: str

    TELEGRAM_BOT_TOKEN_2: str


@lru_cache
def get_settings():
    return Settings()
