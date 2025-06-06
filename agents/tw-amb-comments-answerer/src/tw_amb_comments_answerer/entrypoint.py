import re
import time
from contextlib import asynccontextmanager

from base_agent.ray_entrypoint import BaseAgent
from fastapi import FastAPI
from ray import serve
from redis_client.main import Post, ensure_delay_between_posts, get_redis_db
from tw_amb_comments_answerer.commands import check_answer_is_needed, create_comment_to_comment
from tweetscout_utils.main import create_conversation_string, get_conversation_from_tweet, search_tweets
from twitter_ambassador_utils.main import TwitterAuthClient, create_post


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class TwitterAmbassadorCommentsAnswerer(BaseAgent):
    def __init__(self):
        self.running_tasks = {}

    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None):
        await self.answer_on_project_tweets_comments(goal)

    async def answer_on_project_tweets_comments(
        self,
        goal: str,
    ) -> bool:
        my_username = goal.split(".")[0]
        project_username = goal.split(".")[1]
        keywords = re.findall(r"[a-zA-Z0-9]+", goal.split(".")[2])
        themes = re.findall(r"[a-zA-Z0-9]+", goal.split(".")[3])
        db = get_redis_db()
        try:
            print(f"answer_on_project_tweets_comments {my_username=} {project_username=} {keywords=} {themes=}")

            # Формируем поисковые запросы
            search_queries = keywords + themes
            all_project_comments = []

            # Получаем токен доступа для пользователя
            account_access_token = await TwitterAuthClient.get_access_token(my_username)

            for query in search_queries:
                comments = await search_tweets(
                    access_token=account_access_token, query=f"{query} is:reply to:{project_username}"
                )
                all_project_comments.extend(comments)

            commented_tweets_key = f"answered_comments:{my_username}:{project_username}"
            answered_comments_before = db.get_set(commented_tweets_key)

            tweets_to_comment = [
                tweet for tweet in all_project_comments if tweet.id_str not in answered_comments_before
            ]

            if not tweets_to_comment:
                print("Nothing to comment. Already commented on all relevant tweets")
                return False

            for tweet in tweets_to_comment:
                if await check_answer_is_needed(tweet.full_text, my_username=my_username):
                    conversation = await get_conversation_from_tweet(tweet=tweet)
                    comment_text = await create_comment_to_comment(
                        comment_text=create_conversation_string(conversation),
                        keywords=keywords,
                        themes=themes,
                        my_username=my_username,
                    )

                    await ensure_delay_between_posts(my_username, delay=60)
                    tweet_posted = await create_post(
                        access_token=account_access_token,
                        tweet_text=comment_text,
                        commented_tweet_id=tweet.id_str,
                    )

                    if tweet_posted:
                        post = Post(
                            id=tweet_posted["data"]["id"],
                            text=comment_text,
                            sender_username=my_username,
                            timestamp=int(time.time()),
                            is_reply_to=tweet.id_str,
                        )
                        db.add_user_post(my_username, post)
                        db.add_to_set(commented_tweets_key, tweet.id_str)
                        db.save_tweet_link("answer_on_project_tweets_comments", tweet.id_str)
                        print(f"Posted reply to {tweet.id_str}: {comment_text}")

            return True
        except Exception as error:
            print(f"answer_on_project_tweets_comments error: {my_username=} {error=}")
            raise


def get_agent(agent_args: dict):
    return TwitterAmbassadorCommentsAnswerer.bind(**agent_args)


if __name__ == "__main__":
    serve.run(app, route_prefix="/")
