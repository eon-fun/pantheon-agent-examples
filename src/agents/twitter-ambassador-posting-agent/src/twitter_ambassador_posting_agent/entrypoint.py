import re
from contextlib import asynccontextmanager
from fastapi import FastAPI
from ray import serve
from base_agent import BaseAgent

from tweetscout_utils.main import fetch_user_tweets
from twitter_ambassador_posting_agent.commands import _handle_regular_tweet, _handle_news_tweet, \
    _fetch_quoted_tweet_ids, \
    _find_tweet_for_quote, _handle_quote_tweet
from redis_client.main import db, Post, ensure_delay_between_posts


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class TwitterPostingAgent(BaseAgent):
    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None):
        await self.create_ambassador_tweet(goal)

    async def create_ambassador_tweet(
            self,
            goal: str,
    ) -> Post | None:
        username = goal.split(".")[0]
        keywords = re.findall(r'[a-zA-Z0-9]+', goal.split(".")[1])
        themes = re.findall(r'[a-zA-Z0-9]+', goal.split(".")[2])
        try:
            print(f'create_ambassador_tweet {username=} {keywords=} {themes=}')
            # Get user's previous posts
            my_tweets = db.get_user_posts(username)

            # If user has no tweets, create their first tweet
            if not my_tweets:
                print(f"No previous tweets found for {username}, creating first tweet")
                return await _handle_regular_tweet([], [], username, keywords, themes)

            # Get project tweets
            project_tweets = await fetch_user_tweets(username)

            # Check if last tweet was a news summary
            if not my_tweets[-1].is_news_summary_tweet:
                return await _handle_news_tweet(my_tweets, username, keywords, themes)

            # Check last two tweets for quotes
            if not any(tweet.quoted_tweet_id for tweet in my_tweets[-2:] if len(my_tweets) >= 2):
                quoted_tweet_ids = await _fetch_quoted_tweet_ids(my_tweets)
                tweet_for_quote = await _find_tweet_for_quote(project_tweets, quoted_tweet_ids)

                if tweet_for_quote:
                    return await _handle_quote_tweet(tweet_for_quote, my_tweets, username, keywords, themes)

            # Default to regular tweet if no other conditions met
            return await _handle_regular_tweet(project_tweets, my_tweets, username, keywords, themes)

        except Exception as error:
            print(f'create_ambassador_tweet error: {username=} {type(error)=} {error=}')
            raise error


def get_agent(agent_args: dict):
    return TwitterPostingAgent.bind(**agent_args)


if __name__ == "__main__":
    serve.run(app, route_prefix="/")
