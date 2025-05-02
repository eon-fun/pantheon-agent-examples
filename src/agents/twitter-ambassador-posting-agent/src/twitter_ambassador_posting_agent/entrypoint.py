import re
from contextlib import asynccontextmanager
from fastapi import FastAPI
from ray import serve
from base_agent.ray_entrypoint import BaseAgent
from tweetscout_utils.main import fetch_user_tweets
from twitter_ambassador_posting_agent.commands import handle_regular_tweet, handle_news_tweet, \
    fetch_quoted_tweet_ids, find_tweet_for_quote, handle_quote_tweet, TwitterAuthClient
from redis_client.main import get_redis_db, Post

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
        print(f'Creating posting agent with goal: {goal}')
        await self.create_ambassador_tweet(goal)
        
    async def create_ambassador_tweet(self, goal: str) -> Post | None:
        username = goal.split(".")[0]
        keywords = re.findall(r'[a-zA-Z0-9]+', goal.split(".")[1])
        themes = re.findall(r'[a-zA-Z0-9]+', goal.split(".")[2])
        db = get_redis_db()
        try:
            print(f'Username: {username=}, keywords: {keywords=}, themes: {themes=}')
            print(f'Fetching user\'s previous tweets for user: {username}')
            my_tweets = db.get_user_posts(username)
            account_access_token = await TwitterAuthClient.get_access_token(username)
            
            # If user has no tweets, create their first tweet
            if not my_tweets:
                print(f"No previous tweets found for {username}, creating first tweet")
                return await handle_regular_tweet([], [], username, keywords, themes)
                
            print(f'Fetching project tweets for user: {username}')
            project_tweets = await fetch_user_tweets(username=username)
            
            # Check if last tweet was a news summary with proper null checks
            if my_tweets and hasattr(my_tweets[-1], 'is_news_summary_tweet') and not my_tweets[-1].is_news_summary_tweet:
                return await handle_news_tweet(my_tweets, username, keywords, themes)
                
            # Check last two tweets for quotes with proper null checks
            if len(my_tweets) >= 2 and not any(hasattr(tweet, 'quoted_tweet_id') and tweet.quoted_tweet_id for tweet in my_tweets[-2:]):
                quoted_tweet_ids = await fetch_quoted_tweet_ids(my_tweets)
                tweet_for_quote = await find_tweet_for_quote(project_tweets, quoted_tweet_ids)
                if tweet_for_quote:
                    return await handle_quote_tweet(tweet_for_quote, my_tweets, username, keywords, themes)
                    
            # Default to regular tweet if no other conditions met
            return await handle_regular_tweet(project_tweets, my_tweets, username, keywords, themes)
            
        except Exception as error:
            print(f'create_ambassador_tweet error: {username=} {type(error)=} {error=}')
            raise

def get_agent(agent_args: dict):
    return TwitterPostingAgent.bind(**agent_args)

if __name__ == "__main__":
    serve.run(app, route_prefix="/")