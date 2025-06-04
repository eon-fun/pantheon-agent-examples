import asyncio
from contextlib import asynccontextmanager
from html import escape

import aiohttp
from aiogram.enums import ParseMode
from base_agent.ray_entrypoint import BaseAgent
from fastapi import FastAPI
from openai_request.ray_entrypoint import main as send_openai_request
from ray import serve
from redis_client.ray_entrypoint import main as redis_client
from twitter_summary.config import HEADERS, bot, get_settings
from twitter_summary.src.prompts import AI_PROMPT


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
db = redis_client()


@serve.deployment
@serve.ingress(app)
class TweetProcessor(BaseAgent):
    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None):
        while True:
            try:
                print("🔄 Checking for new tweets...")
                summary = await self.process_new_tweets()
                if summary:
                    print("✅ Tweet summary generated")
                    await bot.send_message(
                        chat_id=get_settings().TELEGRAM_CHANNEL_ID, text=summary, parse_mode=ParseMode.HTML
                    )
                else:
                    print("ℹ️ No new tweets to process")
            except Exception as e:
                print(f"❌ Error processing tweets: {e}")
            await asyncio.sleep(21600)

    def _decode_redis_set(self, redis_set):
        result = set()
        for item in redis_set:
            if isinstance(item, bytes):
                result.add(item.decode("utf-8"))
            else:
                result.add(str(item))
        return result

    async def add_account(self, account):
        try:
            db.r.sadd(get_settings().REDIS_SUBSCRIBED_TWITTER_ACCOUNTS, account)
            print(f"✅ Account added: {account}")
            return True
        except Exception as e:
            print(f"❌ Error adding account {account}: {e}")
            return False

    async def fetch_tweets(self, account):
        try:
            print(f"🔄 Fetching tweets for @{account}...")
            processed_ids = self._decode_redis_set(db.get_set(get_settings().REDIS_LAST_PROCESSED_TWEETS))

            user_url = f"https://api.twitter.com/2/users/by/username/{account}"
            async with aiohttp.ClientSession() as session:
                user_resp = await session.get(user_url, headers=HEADERS)
                user_data = await user_resp.json()

                if "data" not in user_data:
                    print(f"⚠️ No data found for account @{account}")
                    return []

                user_id = user_data["data"]["id"]
                tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
                tweets_resp = await session.get(tweets_url, headers=HEADERS)
                tweets_data = await tweets_resp.json()

                if "data" not in tweets_data:
                    print(f"⚠️ No tweets found for account @{account}")
                    return []

                new_tweets = []
                for tweet in tweets_data["data"]:
                    if tweet["id"] not in processed_ids:
                        tweet_data = {"id": tweet["id"], "account": account, "text": tweet["text"]}
                        new_tweets.append(tweet_data)

                print(f"✅ Fetched {len(new_tweets)} new tweets for @{account}")
                return new_tweets
        except Exception as e:
            print(f"❌ Error fetching tweets for @{account}: {e}")
            return []

    async def process_new_tweets(self):
        try:
            print("🔄 Processing new tweets...")
            accounts = self._decode_redis_set(db.get_set(get_settings().REDIS_SUBSCRIBED_TWITTER_ACCOUNTS))

            if not accounts:
                print("⚠️ No accounts to process")
                return None

            all_tweets = []
            for account in accounts:
                tweets = await self.fetch_tweets(account)
                all_tweets.extend(tweets)

            if all_tweets:
                tweet_texts = [f"@{tweet['account']}: {tweet['text']}" for tweet in all_tweets]
                combined_text = "\n\n".join(tweet_texts)

                messages = [
                    {"role": "system", "content": AI_PROMPT},
                    {"role": "user", "content": f"Here are the tweets:\n\n{combined_text}"},
                ]

                summary = await send_openai_request(messages)
                for tweet in all_tweets:
                    db.r.sadd(get_settings().REDIS_LAST_PROCESSED_TWEETS, tweet["id"])
                print("✅ Tweets processed and summary generated")
                return escape(summary.strip())

            print("ℹ️ No new tweets to summarize")
            return None
        except Exception as e:
            print(f"❌ Error processing tweets: {e}")
            return None


app = TweetProcessor.bind(get_settings())

if __name__ == "__main__":
    serve.run(app, route_prefix="/")
