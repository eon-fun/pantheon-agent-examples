import re
import time
from contextlib import asynccontextmanager

from base_agent.ray_entrypoint import BaseAgent
from fastapi import FastAPI
from ray import serve
from redis_client.main import Post, ensure_delay_between_posts, get_redis_db
from tw_amb_gorilla_marketing.commands import check_tweets_for_gorilla_marketing, create_text_for_gorilla_marketing
from tweetscout_utils.main import search_tweets
from twitter_ambassador_utils.main import TwitterAuthClient, create_post


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class TwitterGorillaMarketingAgent(BaseAgent):
    def __init__(self):
        self.running_tasks = {}

    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None):
        await self.start_gorilla_marketing(goal)

    async def start_gorilla_marketing(self, goal: str) -> bool:
        my_username = goal.split(".")[0]
        keywords = re.findall(r"[a-zA-Z0-9]+", goal.split(".")[1])
        themes = re.findall(r"[a-zA-Z0-9]+", goal.split(".")[2])
        db = get_redis_db()
        try:
            print(f"start_gorilla_marketing {my_username=} {keywords=} {themes=}")

            # Получаем токен доступа один раз для всех запросов
            access_token = await TwitterAuthClient.get_access_token(my_username)

            # Формируем поисковые запросы
            search_queries = keywords + themes  # Не добавляем # к темам

            tweets_dict = {}
            for query in search_queries:
                try:
                    result = await search_tweets(access_token=access_token, query=query)

                    for tweet in result[:3]:
                        if tweet.id_str not in tweets_dict:
                            tweets_dict[tweet.id_str] = tweet
                except Exception as e:
                    print(f"Error searching for query '{query}': {e}")
                    continue  # Продолжаем с другими запросами

            # Получаем уже прокомментированные твиты
            commented_tweets_key = f"gorilla_marketing_answered:{my_username}"
            commented_tweets_before = db.get_set(commented_tweets_key) or set()

            tweets_to_comment = [tweet for tweet in tweets_dict.values() if tweet.id_str not in commented_tweets_before]

            if not tweets_to_comment:
                print("No new tweets to comment on")
                return False

            # Проверяем твиты на релевантность
            good_tweets = await check_tweets_for_gorilla_marketing(
                tweets=tweets_to_comment, keywords=keywords, themes=themes, my_username=my_username
            )

            if not good_tweets:
                print("No relevant tweets found")
                return False

            # Сортируем по количеству лайков
            good_tweets = sorted(good_tweets, key=lambda t: t.favorite_count, reverse=True)

            comments_posted = False
            for tweet in good_tweets[:2]:  # Комментируем только 2 лучших твита
                comment_text = await create_text_for_gorilla_marketing(
                    tweet_text=tweet.full_text, keywords=keywords, themes=themes, my_username=my_username
                )
                await ensure_delay_between_posts(my_username)

                result = await create_post(
                    access_token=access_token,
                    tweet_text=comment_text,
                    commented_tweet_id=tweet.id_str,
                )

                if result and "data" in result and "id" in result["data"]:
                    post = Post(
                        id=result["data"]["id"],
                        text=comment_text,
                        sender_username=my_username,
                        timestamp=int(time.time()),
                        is_reply_to=tweet.id_str,
                    )
                    db.add_user_post(my_username, post)
                    db.add_to_set(commented_tweets_key, tweet.id_str)
                    print(f"Posted comment for tweet {tweet.id_str}: {comment_text}")
                    comments_posted = True

            return comments_posted

        except Exception as error:
            print(f"start_gorilla_marketing error: {my_username=} {error=}")
            return False


def get_agent(agent_args: dict):
    return TwitterGorillaMarketingAgent.bind(**agent_args)


if __name__ == "__main__":
    serve.run(app, route_prefix="/")
