from aiogram import Dispatcher
from pydantic_settings import BaseSettings
from functools import lru_cache

from database.redis.redis_client import RedisDB

db = RedisDB()
dp = Dispatcher()


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = "8039253205:AAEFwlG0c2AmhwIXnqC9Q5TsBo_x-7jM2a0"
    TELEGRAM_CHANNEL_ID: str = "@panteoncryptonews"
    TWITTER_BEARER_TOKEN: str = 'AAAAAAAAAAAAAAAAAAAAAALFxQEAAAAAccmjfpy9O9AoKsiWm3EiKRmlYW0%3DKxQgwMPoButLHfAL1Zoledy4bdko6ufQNLTQuxDpCfZxfgthkI'

    REDIS_LAST_PROCESSED_TWEETS: str = "last_processed_tweets"
    REDIS_SUBSCRIBED_TWITTER_ACCOUNTS: str = "subscribed_twitter_accounts"
    REDIS_TWEETS_TO_PROCESS: str = "tweets_to_process"


@lru_cache
def get_settings():
    return Settings()


HEADERS = {"Authorization": f"Bearer {get_settings().TWITTER_BEARER_TOKEN}"}

