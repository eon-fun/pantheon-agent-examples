import ray
import aiohttp
import json
from html import escape
from database.redis.redis_client import RedisDB
from services.ai_tools.openai_client import send_openai_request

TWITTER_PROMPT = """
You are a social media analyst and news summarizer for a cryptocurrency and celebrity news channel. Your task is to monitor tweets and create concise summaries that highlight key events, their potential consequences, and the involved parties.

When summarizing tweets:
- Combine related tweets into one coherent summary.
- Clearly state the main events or announcements, e.g., "Famous investor John Doe announces plans to buy BTC."
- Explain possible implications or market reactions, e.g., "This could lead to increased confidence in BTC."
- Include usernames of involved people or accounts when relevant, e.g., "@johndoe."
- If the tweets reflect a conflict or interaction, summarize the core of the conflict, e.g., "A heated exchange between @star1 and @star2 about recent controversies."
- Use engaging and clear language suitable for Telegram posts in English. Use HTML formatting for beautify text.

End the summary with an engaging closing line like "Stay tuned for updates! 🚀" or similar.
"""
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAALFxQEAAAAAccmjfpy9O9AoKsiWm3EiKRmlYW0%3DKxQgwMPoButLHfAL1Zoledy4bdko6ufQNLTQuxDpCfZxfgthkI'


@ray.remote
class TweetProcessor:
    def __init__(self):
        self.db = RedisDB()
        self.headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
        print("✅ TweetProcessor initialized")

    def _decode_redis_set(self, redis_set):
        """Helper function to decode Redis set items."""
        result = set()
        for item in redis_set:
            if isinstance(item, bytes):
                result.add(item.decode('utf-8'))
            else:
                result.add(str(item))
        return result

    async def add_account(self, account):
        """Adds a Twitter account to the subscribed list."""
        try:
            self.db.r.sadd("subscribed_twitter_accounts", account)
            print(f"✅ Account added: {account}")
            return True
        except Exception as e:
            print(f"❌ Error adding account {account}: {e}")
            return False

    async def fetch_tweets(self, account):
        """Fetches tweets from a given account."""
        try:
            print(f"🔄 Fetching tweets for @{account}...")
            processed_ids = self._decode_redis_set(self.db.get_set("last_processed_tweets"))

            user_url = f"https://api.twitter.com/2/users/by/username/{account}"
            async with aiohttp.ClientSession() as session:
                user_resp = await session.get(user_url, headers=self.headers)
                user_data = await user_resp.json()

                if "data" not in user_data:
                    print(f"⚠️ No data found for account @{account}")
                    return []

                user_id = user_data["data"]["id"]
                tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
                tweets_resp = await session.get(tweets_url, headers=self.headers)
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
        """Processes new tweets and generates a summary."""
        try:
            print("🔄 Processing new tweets...")
            accounts = self._decode_redis_set(self.db.get_set("subscribed_twitter_accounts"))

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
                    {"role": "system", "content": TWITTER_PROMPT},
                    {"role": "user", "content": f"Here are the tweets:\n\n{combined_text}"}
                ]

                summary = await send_openai_request(messages)
                for tweet in all_tweets:
                    self.db.r.sadd("last_processed_tweets", tweet['id'])
                print("✅ Tweets processed and summary generated")
                return escape(summary.strip())

            print("ℹ️ No new tweets to summarize")
            return None
        except Exception as e:
            print(f"❌ Error processing tweets: {e}")
            return None
