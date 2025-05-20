from pydantic_settings import BaseSettings
from functools import lru_cache

from telethon import TelegramClient

from database.redis.redis_client import RedisDB

db = RedisDB()


class Settings(BaseSettings):
    API_ID: str
    API_HASH: str
    SESSION_NAME: str
    REDIS_MESSAGES_KEY: str
    BOT_COMMAND: str


@lru_cache
def get_settings():
    return Settings()



def create_telethon_client():
    return TelegramClient(
        get_settings().SESSION_NAME,
        int(get_settings().API_ID),
        get_settings().API_HASH
    )


def get_telethon_client():
    return create_telethon_client()
