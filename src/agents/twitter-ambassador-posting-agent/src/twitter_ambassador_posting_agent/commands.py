import time
from datetime import datetime, timedelta

from tweetscout_utils.main import Tweet
from redis_client.main import get_redis_db, Post
from twitter_ambassador_utils.main import create_post, TwitterAuthClient
from tweetscout_utils.main import search_tweets
from send_openai_request.main import send_openai_request

db = get_redis_db()


async def add_blank_lines(text) -> str:
    messages = [
        {
            "role": "system",
            "content": """You are a text formatter. Your task is only to format the text. 
The text should be split into several paragraphs with a blank line between them. 
Do not change the content of the text, just insert blank lines to divide it into paragraphs.

EXAMPLE INPUT:
Discover $NFNT, where sci-fi meets reality! With NFINITY, even your dog's to-do list becomes autonomous. Who needs thumbs? Unleash the hyper-advanced AI bot and watch it fetch not just sticks but ROI. 🐶🔥 #NFINITY 

EXAMPLE OUTPUT:
Discover $NFNT, where sci-fi meets reality!

With NFINITY, even your dog's to-do list becomes autonomous.

Who needs thumbs? Unleash the hyper-advanced AI bot and watch it fetch not just sticks but ROI. 🐶🔥 

#NFINITY @nfinityAI 🚀
"""
        },
        {
            "role": "user",
            "content": text
        }
    ]

    formatter_prompt = (
        "You are a text formatter. Your task is only to format the text. \n"
        "The text should be split into several paragraphs with a blank line between them. \n"
        "Do not change the content of the text, just insert blank lines to divide it into paragraphs.\n\n"
        "EXAMPLE INPUT:\n"
        "Discover $NFNT, where sci-fi meets reality! With NFINITY, even your dog's to-do list becomes autonomous. Who needs thumbs? Unleash the hyper-advanced AI bot and watch it fetch not just sticks but ROI. 🐶🔥 #NFINITY \n\n"
        "EXAMPLE OUTPUT:\n"
        "Discover $NFNT, where sci-fi meets reality!\n\n"
        "With NFINITY, even your dog's to-do list becomes autonomous.\n\n"
        "Who needs thumbs? Unleash the hyper-advanced AI bot and watch it fetch not just sticks but ROI. 🐶🔥 \n\n"
        "#NFINITY @nfinityAI 🚀\n\n"
        f"{text}"
    )
    text = await send_openai_request(messages=messages, temperature=1.0)
    print(f'Tweet validating 2 {text}')
    return text


async def format_text(text: str) -> str:
    text = await add_blank_lines(text)
    for _ in range(20):
        if len(text) <= 280:
            return text
        messages = [
            {
                "role": "system",
                "content": "You are a text shortener. Your task is to reduce the text length, keeping "
                           "its meaning and style unchanged. You can remove some sentences as long as it "
                           "doesn't harm the overall meaning of the text. Also remove emojis. REMOVE HASHTAGS"
            },
            {
                "role": "user",
                "content": text
            }
        ]

        system_prompt = (
            "You are a text shortener. Your task is to reduce the text length, keeping "
            "its meaning and style unchanged. You can remove some sentences as long as it "
            "doesn't harm the overall meaning of the text. Also remove emojis. REMOVE HASHTAGS\n\n"
            f"{text}"
        )
        text = await send_openai_request(messages=messages, temperature=1.0)

        print(f'Tweet validating 1 {text}')
        text = await add_blank_lines(text)

    raise ValueError('Generated text is too long')


async def _handle_quote_tweet(project_tweet: Tweet, my_tweets: list[Post], username: str, keywords: list[str],
                              themes: list[str]) -> Post:
    """Tweet about project with quote project tweet"""
    tweet_text = await _create_quoted_tweet(
        tweet_for_quote=project_tweet.full_text,
        my_tweets=[tweet.text for tweet in my_tweets],
        keywords=keywords,
        themes=themes
    )
    result = await create_post(
        access_token=await TwitterAuthClient.get_access_token(username),
        tweet_text=tweet_text,
        quote_tweet_id=project_tweet.id_str,
    )
    if result is None or 'data' not in result or 'id' not in result['data']:
        print(f"create_post did not return the expected data: {result}")
        return

    post = Post(
        id=result['data']['id'],
        text=tweet_text,
        sender_username=username,
        quoted_tweet_id=project_tweet.id_str,
        timestamp=int(time.time())
    )
    db.add_user_post(username, post)
    db.save_tweet_link('create_ambassador_tweet', result['data']['id'])
    return post


async def _handle_regular_tweet(project_tweets: list[Tweet], my_tweets: list[Post], username: str, keywords: list[str],
                                themes: list[str]) -> Post:
    """Regular tweet about project"""
    tweet_text = await _create_tweet(
        project_tweets=[tweet.full_text for tweet in project_tweets],
        my_tweets=[tweet.text for tweet in my_tweets],
        keywords=keywords,
        username=username,
        themes=themes
    )

    result = await create_post(
        access_token=await TwitterAuthClient.get_access_token(username),
        tweet_text=tweet_text,
    )
    if result is None or 'data' not in result or 'id' not in result['data']:
        print(f"create_post did not return the expected data: {result}")
        return

    post = Post(
        id=result['data']['id'],
        text=tweet_text,
        sender_username=username,
        timestamp=int(time.time())
    )
    db.add_user_post(username, post)
    db.save_tweet_link('create_ambassador_tweet', result['data']['id'])
    return post


async def _handle_news_tweet(my_tweets: list[Post], username: str, keywords: list[str], themes: list[str]) -> Post:
    """Tweet about news using project context"""
    since = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d_%H:%M:%S_UTC")

    # Используем keywords и themes для поиска новостей
    search_queries = keywords + [f"#{theme}" for theme in themes]
    all_news_tweets = []

    for query in search_queries:
        news = await search_tweets(f"{query} min_faves:100 -filter:replies lang:en since:{since}")
        all_news_tweets.extend(tweet.full_text for tweet in news if len(tweet.full_text) > 200)

    tweet_text = await _create_news_tweet(
        my_tweets=[tweet.text for tweet in my_tweets],
        news_tweets=all_news_tweets,
        keywords=keywords,
        username=username,
        themes=themes
    )

    result = await create_post(
        access_token=await TwitterAuthClient.get_access_token(username),
        tweet_text=tweet_text,
    )
    if result is None or 'data' not in result or 'id' not in result['data']:
        print(f"create_post did not return the expected data: {result}")
        return

    post = Post(
        id=result['data']['id'],
        text=tweet_text,
        sender_username=username,
        timestamp=int(time.time()),
        is_news_summary_tweet=True,
    )
    db.add_user_post(username, post)
    db.save_tweet_link('create_ambassador_tweet', result['data']['id'])
    return post


async def _create_tweet(
        project_tweets: list[str],
        my_tweets: list[str],
        keywords: list[str],
        themes: list[str],
        username: str,
        prompt: str = ""
) -> str:
    print('generate tweet')
    messages = [
        {"role": "system", "content": prompt},
    ]
    result = await send_openai_request(messages=messages, temperature=1.0)
    print(f'Created prompt: {prompt=}')
    return await format_text(result)


async def _create_quoted_tweet(
        tweet_for_quote: str,
        my_tweets: list[str],
        keywords: list[str],
        themes: list[str],
        username: str,
        prompt: str = ""
) -> str:
    print(f'generate quote tweet: {tweet_for_quote=}')
    messages = [
        {"role": "system", "content": prompt},
    ]
    result = await send_openai_request(messages=messages, temperature=1.0)
    print(f'Created prompt: {prompt=}')
    return await format_text(result)


async def _create_news_tweet(
        news_tweets: list[str],
        my_tweets: list[str],
        keywords: list[str],
        themes: list[str],
        username: str,
        prompt: str = ""
) -> str:
    print(f'_create_news_tweet: {news_tweets=}')
    messages = [
        {"role": "system", "content": prompt},
    ]
    result = await send_openai_request(messages=messages, temperature=1.0)
    print(f'Created prompt: {prompt=}')
    return await format_text(result)


async def _fetch_quoted_tweet_ids(my_tweets: list[Post]) -> set:
    quoted_tweet_ids = set()
    for my_tweet in my_tweets:
        if my_tweet.quoted_tweet_id:
            quoted_tweet_ids.add(my_tweet.quoted_tweet_id)
    return quoted_tweet_ids


async def _find_tweet_for_quote(project_tweets: list, quoted_tweet_ids: set) -> Tweet | None:
    for project_tweet in project_tweets:
        if (not project_tweet.retweeted_status and project_tweet.id_str not in quoted_tweet_ids) or (
            project_tweet.retweeted_status and project_tweet.retweeted_status.id_str not in quoted_tweet_ids
        ):
            return project_tweet
    return None
