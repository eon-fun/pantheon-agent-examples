import re
from contextlib import asynccontextmanager

from base_agent.ray_entrypoint import BaseAgent
from fastapi import FastAPI
from ray import serve
from redis_client.main import Post, get_redis_db
from tweetscout_utils.main import fetch_user_tweets
from twitter_ambassador_posting_agent.commands import (
    TwitterAuthClient,
    _fetch_quoted_tweet_ids,
    _find_tweet_for_quote,
    _handle_news_tweet,
    _handle_quote_tweet,
    _handle_regular_tweet,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class TwitterPostingAgent(BaseAgent):
    def __init__(self):
        self.running_tasks = {}

    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None):
        print(f"Creating posting agent with goal: {goal}")
        await self.create_ambassador_tweet(goal)

    async def create_ambassador_tweet(self, goal: str) -> Post | None:
        username = goal.split(".")[0]
        keywords = re.findall(r"[a-zA-Z0-9]+", goal.split(".")[1])
        themes = re.findall(r"[a-zA-Z0-9]+", goal.split(".")[2])
        db = get_redis_db()
        try:
            print(f"Username: {username=}, keywords: {keywords=}, themes: {themes=}")
            print(f"Fetching user's previous tweets for user: {username}")
            my_tweets = db.get_user_posts(username)
            account_access_token = await TwitterAuthClient.get_access_token(username)

            # If user has no tweets, create their first tweet
            if not my_tweets:
                print(f"No previous tweets found for {username}, creating first tweet")
                return await _handle_regular_tweet([], [], username, keywords, themes)

            print(f"Fetching project tweets for user: {username}")
            project_tweets = await fetch_user_tweets(username=username)

            # Check if last tweet was a news summary
            if (
                my_tweets
                and hasattr(my_tweets[-1], "is_news_summary_tweet")
                and not my_tweets[-1].is_news_summary_tweet
            ):
                return await _handle_news_tweet(my_tweets, username, keywords, themes)

            # Check last two tweets for quotes
            if len(my_tweets) >= 2 and not any(
                hasattr(tweet, "quoted_tweet_id") and tweet.quoted_tweet_id for tweet in my_tweets[-2:]
            ):
                quoted_tweet_ids = await _fetch_quoted_tweet_ids(my_tweets)
                tweet_for_quote = await _find_tweet_for_quote(project_tweets, quoted_tweet_ids)
                if tweet_for_quote:
                    return await _handle_quote_tweet(tweet_for_quote, my_tweets, username, keywords, themes)

            # Default to regular tweet if no other conditions met
            return await _handle_regular_tweet(project_tweets, my_tweets, username, keywords, themes)

        except Exception as error:
            print(f"create_ambassador_tweet error: {username=} {type(error)=} {error=}")
            raise


def get_agent(agent_args: dict):
    return TwitterPostingAgent.bind(**agent_args)


if __name__ == "__main__":
    serve.run(app, route_prefix="/")
