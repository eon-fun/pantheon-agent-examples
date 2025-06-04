from functools import lru_cache

from aiogram import Bot, Dispatcher
from database.redis.redis_client import RedisDB  # Вынести в либу
from pydantic_settings import BaseSettings

db = RedisDB()
dp = Dispatcher()


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHANNEL_ID: str
    TWITTER_BEARER_TOKEN: str

    REDIS_LAST_PROCESSED_TWEETS: str
    REDIS_SUBSCRIBED_TWITTER_ACCOUNTS: str


@lru_cache
def get_settings():
    return Settings()


HEADERS = {"Authorization": f"Bearer {get_settings().TWITTER_BEARER_TOKEN}"}
bot = Bot(token=get_settings().TELEGRAM_BOT_TOKEN)
