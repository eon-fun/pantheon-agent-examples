import asyncio
from ai_twitter_summary.main import TweetProcessor, summarize_tweets
from redis_client.main import get_redis_db


async def main():
    processor = TweetProcessor()

    tweets = await processor.process_new_tweets()
    if tweets:
        summary = await summarize_tweets(tweets)
        print(f"Generated Summary:\n{summary}")

    get_redis_db().r.sadd("subscribed_twitter_accounts", "VitalikButerin")

asyncio.run(main())
