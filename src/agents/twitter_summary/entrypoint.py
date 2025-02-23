from html import escape

import aiohttp
from contextlib import asynccontextmanager
from fastapi import FastAPI
from ray import serve
from agent.ray_entrypoint import BaseAgent

from agents.twitter_summary.src.config import db, HEADERS, get_settings
from agents.twitter_summary.src.prompts import AI_PROMPT
from services.ai_connectors.openai_client import send_openai_request


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class TweetProcessor(BaseAgent):
    def _decode_redis_set(self, redis_set):
        result = set()
        for item in redis_set:
            if isinstance(item, bytes):
                result.add(item.decode('utf-8'))
            else:
                result.add(str(item))
        return result

    async def add_account(self, account):
        try:
            db.r.sadd("subscribed_twitter_accounts", account)
            print(f"✅ Account added: {account}")
            return True
        except Exception as e:
            print(f"❌ Error adding account {account}: {e}")
            return False

    async def fetch_tweets(self, account):
        try:
            print(f"🔄 Fetching tweets for @{account}...")
            processed_ids = self._decode_redis_set(db.get_set("last_processed_tweets"))

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
            accounts = self._decode_redis_set(db.get_set("subscribed_twitter_accounts"))

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
                    {"role": "user", "content": f"Here are the tweets:\n\n{combined_text}"}
                ]

                summary = await send_openai_request(messages)
                for tweet in all_tweets:
                    db.r.sadd("last_processed_tweets", tweet['id'])
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
