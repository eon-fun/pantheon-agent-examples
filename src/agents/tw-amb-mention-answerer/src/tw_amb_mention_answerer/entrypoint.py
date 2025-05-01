import time
import re

from contextlib import asynccontextmanager
from fastapi import FastAPI
from ray import serve
from base_agent.ray_entrypoint import BaseAgent
from twitter_ambassador_utils.main import TwitterAuthClient, create_post
from tweetscout_utils.main import get_conversation_from_tweet, create_conversation_string, search_tweets
from redis_client.main import Post, ensure_delay_between_posts, get_redis_db
from tw_amb_mention_answerer.commands import check_mention_needs_reply, create_mention_reply


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class TwitterMentionsMonitor(BaseAgent):
    def __init__(self):
        self.running_tasks = {}

    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None):
        await self.respond_to_mentions(goal)

    async def respond_to_mentions(self, goal: str) -> bool:
        parts = goal.split(".")
        my_username = parts[0]
        keywords = re.findall(r'[a-zA-Z0-9]+', parts[1]) if len(parts) > 1 else []
        hashtags = re.findall(r'[a-zA-Z0-9]+', parts[2]) if len(parts) > 2 else []

        db = get_redis_db()
        try:
            print(f'respond_to_mentions {my_username=} {keywords=} {hashtags=}')
            account_access_token = await TwitterAuthClient.get_access_token(my_username)

            mentions = await search_tweets(
                access_token=account_access_token,
                query=f"@{my_username} -is:retweet"  # Находит упоминания пользователя, исключая ретвиты
            )

            responded_mentions_key = f'responded_mentions:{my_username}'
            previously_responded = db.get_set(responded_mentions_key) or set()

            new_mentions = [
                mention for mention in mentions
                if mention.id_str not in previously_responded
            ]

            if not new_mentions:
                print("No new mentions to respond to")
                return False

            for mention in new_mentions:
                if await check_mention_needs_reply(mention.full_text, my_username):
                    conversation = await get_conversation_from_tweet(access_token=account_access_token, tweet=mention)
                    conversation_text = create_conversation_string(conversation)

                    reply_text = await create_mention_reply(
                        conversation_text=conversation_text,
                        keywords=keywords,
                        hashtags=hashtags,
                        my_username=my_username
                    )

                    await ensure_delay_between_posts(my_username, delay=120)

                    tweet_posted = await create_post(
                        access_token=account_access_token,
                        tweet_text=reply_text,
                        commented_tweet_id=mention.id_str,
                    )

                    if tweet_posted:
                        post = Post(
                            id=tweet_posted['data']['id'],
                            text=reply_text,
                            sender_username=my_username,
                            timestamp=int(time.time()),
                            is_reply_to=mention.id_str,
                        )
                        db.add_user_post(my_username, post)
                        db.add_to_set(responded_mentions_key, mention.id_str)
                        db.save_tweet_link('respond_to_mentions', mention.id_str)
                        print(f'Posted reply to mention {mention.id_str}: {reply_text}')

            return True

        except Exception as error:
            print(f'respond_to_mentions error: {my_username=} {error=}')
            raise


def get_agent(agent_args: dict):
    return TwitterMentionsMonitor.bind(**agent_args)


if __name__ == "__main__":
    serve.run(app, route_prefix="/")
