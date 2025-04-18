import random
import time
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from ray import serve
from base_agent.ray_entrypoint import BaseAgent

from twitter_ambassador_utils.main import create_post, TwitterAuthClient
from tweetscout_utils.main import fetch_user_tweets
from twitter_ambassador_commentator.commands import create_comment_to_post
from redis_client.main import get_redis_db, ensure_delay_between_posts, Post


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class TwitterCommentatorAgent(BaseAgent):
    def __init__(self):
        self.running_tasks = {}

    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None):
        await self.comment_users_tweet_posts(goal)
        if goal not in self.running_tasks or self.running_tasks[goal].done():
            self.running_tasks[goal] = asyncio.create_task(self.schedule_next_run(goal))

    async def schedule_next_run(self, goal: str):
        while True:
            timeout = random.randint(1800, 3600)
            await asyncio.sleep(timeout)
            print(f"Scheduled rerun for goal: {goal}")
            await self.comment_users_tweet_posts(goal)

    async def comment_users_tweet_posts(
            self,
            goal: str,
    ):
        my_username = goal.split(".")[0]
        project_username = goal.split(".")[1]
        db = get_redis_db()
        try:
            print(f'comment_users_tweet_posts_processor {my_username=} {project_username=}')
            project_tweets = await fetch_user_tweets(project_username)
            commented_tweets_key = f'commented_tweets:{my_username}:{project_username}'
            commented_tweets_before = db.get_set(commented_tweets_key)

            tweets_to_comment = [
                tweet for tweet in project_tweets if tweet.id_str not in commented_tweets_before
            ]

            if not tweets_to_comment:
                return "Nothing to comment. You have already commented every tweet"

            commented_tweets = []

            for tweet in tweets_to_comment[:1]:
                comment_text = await create_comment_to_post(tweet.full_text, my_username)
                await ensure_delay_between_posts(my_username)
                tweet_posted = await create_post(
                    access_token=await TwitterAuthClient.get_access_token(my_username),
                    tweet_text=comment_text,
                    commented_tweet_id=tweet.id_str,
                )
                if tweet_posted:
                    post = Post(
                        id=tweet_posted['data']['id'],
                        text=comment_text,
                        sender_username=my_username,
                        timestamp=int(time.time()),
                        is_reply_to=tweet.id_str,
                    )
                    db.add_user_post(my_username, post)
                    commented_tweets.append(tweet)
                    db.add_to_set(commented_tweets_key, tweet.id_str)
                    db.save_tweet_link('comment_users_tweet_posts', tweet.id_str)

            return True
        except BaseException as error:
            print(f'comment_users_tweet_posts error: {my_username=} {error=}')
            raise error


def get_agent(agent_args: dict):
    return TwitterCommentatorAgent.bind(**agent_args)


if __name__ == "__main__":
    serve.run(app, route_prefix="/")
