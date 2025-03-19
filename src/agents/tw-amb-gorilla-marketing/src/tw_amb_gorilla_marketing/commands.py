from typing import Sequence

from twitter_ambassador_utils.main import set_like, TwitterAuthClient
from tweetscout_utils.main import Tweet, search_tweets
from send_openai_request.main import send_openai_request


async def find_tweets_for_gorilla_marketing() -> Sequence[Tweet]:
    tweets_dict = {}
    search_terms = [
        "decentralized AI",
        "AI Web3",
        "AI-driven crypto",
        "AI agent web3",
        "nfinityAI",
        "$NFNT",
    ]
    for search_term in search_terms:
        result = await search_tweets(
            f"{search_term} -filter:replies min_faves:5 lang:en -from:nfinityAI"
        )
        for tweet in result[:3]:
            if tweet.id_str not in tweets_dict:
                tweets_dict[tweet.id_str] = tweet

    return list(tweets_dict.values())


async def check_tweets_for_gorilla_marketing(
        tweets: Sequence[Tweet],
        keywords: list[str],
        themes: list[str],
        my_username: str,
        prompt: str = ""
) -> Sequence[Tweet]:
    good_tweets = []

    for tweet in tweets:
        formatted_prompt = prompt.format(
            tweet_text=tweet.full_text,
            keywords=keywords,
            themes=themes
        )

        messages = [
            {
                "role": "system",
                "content": formatted_prompt
            }
        ]

        result = await send_openai_request(messages=messages, temperature=1.0)

        if 'true' in result.lower():
            good_tweets.append(tweet)

    print(f'Count good tweets {len(good_tweets)=} {good_tweets}')
    return good_tweets


async def create_text_for_gorilla_marketing(
        tweet_text: str,
        keywords: list[str],
        themes: list[str],
        my_username: str,
        prompt: str = ""
) -> str:
    formatted_prompt = prompt.format(
        tweet_text=tweet_text,
        keywords=keywords,
        themes=themes
    )

    messages = [
        {
            "role": "system",
            "content": formatted_prompt
        }
    ]
    result = await send_openai_request(messages=messages, temperature=1.0)
    return result
