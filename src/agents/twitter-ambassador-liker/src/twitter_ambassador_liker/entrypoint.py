import asyncio
from random import randint
import re

from contextlib import asynccontextmanager
from fastapi import FastAPI
from ray import serve
from base_agent.ray_entrypoint import BaseAgent

from twitter_ambassador_utils.main import set_like, TwitterAuthClient
from tweetscout_utils.main import search_tweets
from redis_client.main import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class TwitterLikerAgent(BaseAgent):
    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None):
        await self.set_likes(goal)

    async def set_likes(
            self,
            goal: str
    ) -> bool:
        my_username = goal.split(".")[0]
        keywords = re.findall(r'[a-zA-Z0-9]+', goal.split(".")[1])
        themes = re.findall(r'[a-zA-Z0-9]+', goal.split(".")[2])
        try:
            print(f'set_likes {my_username=} {keywords=} {themes=}')

            # Формируем поисковые запросы из keywords и themes
            search_queries = keywords + [f"#{theme}" for theme in themes]

            tweets_dict = {}
            for query in search_queries:
                # Добавляем дополнительные параметры поиска
                result = await search_tweets(
                    f"{query} -filter:replies min_faves:20 lang:en"
                )
                for tweet in result[:2]:  # Берем только первые 2 твита для каждого запроса
                    if tweet.id_str not in tweets_dict:
                        tweets_dict[tweet.id_str] = tweet

            # Получаем уже лайкнутые твиты
            user_likes_key = f'user_likes:{my_username}'
            likes_tweet_before = db.get_set(user_likes_key)

            tweets_to_like = [
                tweet for tweet in tweets_dict.values()
                if tweet.id_str not in likes_tweet_before
            ]

            if not tweets_to_like:
                print(f"Nothing to like {my_username=}. You have already liked every tweet")
                return False

            for tweet in tweets_to_like[:randint(1, 3)]:  # Лайкаем случайное количество твитов
                await asyncio.sleep(randint(10, 40))  # Случайная задержка
                result = await set_like(
                    token=await TwitterAuthClient.get_access_token(my_username),
                    tweet_id=tweet.id_str,
                    user_id=TwitterAuthClient.get_static_data(my_username)['id'],
                )
                if result.get('data', {}).get('liked'):
                    print(f'Liked tweet: {my_username=} {tweet.id_str=}')
                    db.add_to_set(user_likes_key, tweet.id_str)

            return True

        except Exception as error:
            print(f'set_likes error: {my_username=} {error=}')
            return False


app = TwitterLikerAgent.bind()


if __name__ == "__main__":
    serve.run(app, route_prefix="/")
