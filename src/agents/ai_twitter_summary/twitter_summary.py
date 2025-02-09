import ray
import asyncio
import aiohttp
from html import escape
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from database.redis.redis_client import RedisDB
from services.ai_connectors.openai_client import send_openai_request

# Constants
TELEGRAM_BOT_TOKEN = "8039253205:AAEFwlG0c2AmhwIXnqC9Q5TsBo_x-7jM2a0"
TELEGRAM_CHANNEL_ID = "@panteoncryptonews"
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAALFxQEAAAAAccmjfpy9O9AoKsiWm3EiKRmlYW0%3DKxQgwMPoButLHfAL1Zoledy4bdko6ufQNLTQuxDpCfZxfgthkI'

REDIS_LAST_PROCESSED_TWEETS = "last_processed_tweets"
REDIS_SUBSCRIBED_TWITTER_ACCOUNTS = "subscribed_twitter_accounts"
REDIS_TWEETS_TO_PROCESS = "tweets_to_process"

AI_PROMPT = """
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

# Initialize Redis and Telegram
db = RedisDB()
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


# @ray.remote
class TweetProcessor:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

    async def _fetch_with_retry(self, url):
        """Fetch data from Twitter API with retries."""
        for attempt in range(5):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers) as resp:
                        resp.raise_for_status()
                        return await resp.json()
            except Exception as e:
                if attempt == 4:
                    raise e
                await asyncio.sleep(2)

    async def fetch_tweets(self, account, processed_tweet_ids):
        """Fetch tweets for a given account."""
        try:
            print(f"🔍 Fetching tweets for @{account}")
            processed_ids = {str(id) for id in processed_tweet_ids}

            user_url = f"https://api.twitter.com/2/users/by/username/{account}"
            user_data = await self._fetch_with_retry(user_url)

            if "data" not in user_data:
                print(f"⚠️ Could not get user_id for @{account}")
                return []

            user_id = user_data["data"]["id"]
            tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            tweets_data = await self._fetch_with_retry(tweets_url)

            if "data" not in tweets_data:
                print(f"⚠️ No tweets available for @{account}")
                return []

            new_tweets = []
            for tweet in tweets_data["data"]:
                if str(tweet["id"]) not in processed_ids:
                    tweet_data = {
                        "id": str(tweet["id"]),
                        "account": str(account),
                        "text": str(tweet["text"])
                    }
                    new_tweets.append(tweet_data)

            return new_tweets

        except Exception as e:
            print(f"❌ Error for @{account}: {e}")
            return []

    async def process_new_tweets(self):
        """Fetch and process tweets from all subscribed accounts."""
        accounts = self.get_redis_set_items(REDIS_SUBSCRIBED_TWITTER_ACCOUNTS)
        processed_tweet_ids = self.get_redis_set_items(REDIS_LAST_PROCESSED_TWEETS)

        all_tweets = []
        for account in accounts:
            tweets = await self.fetch_tweets(account, processed_tweet_ids)
            all_tweets.extend(tweets)

        return all_tweets

    def get_redis_set_items(self, redis_key):
        """Helper function to get items from Redis set and convert them to strings."""
        items = db.get_set(redis_key)
        return {item.decode('utf-8') if isinstance(item, bytes) else str(item) for item in items}


async def summarize_tweets(tweets):
    """Summarize tweets using AI."""
    if not tweets:
        return None

    tweet_texts = [f"@{tweet['account']}: {tweet['text']}" for tweet in tweets]
    combined_text = "\n\n".join(tweet_texts)
    messages = [
        {"role": "system", "content": AI_PROMPT},
        {"role": "user", "content": f"Here are the tweets:\n\n{combined_text}"}
    ]

    try:
        summary = await send_openai_request(messages)
        return escape(summary.strip())
    except Exception as e:
        print(f"❌ Summary creation error: {e}")
        return None


async def periodic_task():
    """Periodic task to fetch and process tweets."""
    processor = TweetProcessor.remote()
    while True:
        try:
            print("🔄 Checking for new tweets...")
            new_tweets_future = processor.process_new_tweets.remote()
            new_tweets = await ray.get(new_tweets_future)

            if new_tweets:
                summary = await summarize_tweets(new_tweets)
                if summary:
                    try:
                        await bot.send_message(
                            chat_id=TELEGRAM_CHANNEL_ID,
                            text=summary,
                            parse_mode=ParseMode.HTML
                        )
                        print("✅ Summary sent successfully")

                        # Update processed tweets in Redis
                        for tweet in new_tweets:
                            db.r.sadd(REDIS_LAST_PROCESSED_TWEETS, str(tweet['id']))
                    except Exception as e:
                        print(f"❌ Message sending error: {e}")
                else:
                    print("⚠️ No summary generated")
            else:
                print("ℹ️ No new tweets to process")

        except Exception as e:
            print(f"❌ Periodic task error: {str(e)}")
        await asyncio.sleep(30)


async def main():
    """Main function to start the bot and periodic task."""
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
        print("Ray initialized successfully!")

    asyncio.create_task(periodic_task())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
