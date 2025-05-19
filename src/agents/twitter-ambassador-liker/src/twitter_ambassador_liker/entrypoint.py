import asyncio
from random import randint
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI
from ray import serve
from base_agent.ray_entrypoint import BaseAgent
from twitter_ambassador_utils.main import set_like, TwitterAuthClient
from tweetscout_utils.main import search_tweets
from redis_client.main import get_redis_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

@serve.deployment
@serve.ingress(app)
class TwitterLikerAgent(BaseAgent):
    def __init__(self):
        self.running_tasks = {}
        
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
        db = get_redis_db()
        try:
            print(f'set_likes {my_username=} {keywords=} {themes=}')
            
            # Используем и ключевые слова, и темы для поиска
            search_queries = keywords + themes
            
            # Получаем уже лайкнутые твиты
            user_likes_key = f'user_likes:{my_username}'
            likes_tweet_before = db.get_set(user_likes_key)
            
            tweets_dict = {}
            account_access_token = await TwitterAuthClient.get_access_token(my_username)
            
            for query in search_queries:
                try:
                    # Максимально упрощенный запрос - просто само ключевое слово
                    simple_query = query
                    result = await search_tweets(query=simple_query)
                    
                    # Сохраняем все найденные твиты без фильтрации
                    for tweet in result:
                        if tweet.id_str not in tweets_dict:
                            tweets_dict[tweet.id_str] = tweet
                            
                except Exception as e:
                    print(f"Error searching for {query}: {e}")
                    continue
            
            tweets_to_like = [
                tweet for tweet in tweets_dict.values()
                if tweet.id_str not in likes_tweet_before
            ]
            
            if not tweets_to_like:
                print(f"Nothing to like {my_username=}. You have already liked every tweet")
                return False
                
            for tweet in tweets_to_like[:randint(1, 3)]:
                await asyncio.sleep(randint(10, 40))
                result = await set_like(
                    token=account_access_token,
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

def get_agent(agent_args: dict):
    return TwitterLikerAgent.bind(**agent_args)

if __name__ == "__main__":
    serve.run(app, route_prefix="/")