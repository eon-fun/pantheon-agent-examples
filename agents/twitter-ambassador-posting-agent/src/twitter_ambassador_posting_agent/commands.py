import re
import time

from redis_client.main import Post, get_redis_db
from send_openai_request.main import send_openai_request
from tweetscout_utils.main import Tweet, search_tweets
from twitter_ambassador_utils.main import TwitterAuthClient, create_post

db = get_redis_db()

PROMPT_FOR_TWEET = """ DONT USE HASHTAG You are an autonomous AI Twitter Ambassador and enthusiast. Your task is to generate engaging content using the provided knowledge base context.

Guidelines for tweet creation:
1. Length: Maximum 260 characters
2. Style:
   - Bullish and positive tone
   - Professional but casual language
   - Natural, human-like writing
   - Humor or light sarcasm when appropriate
   - No emojis

3. Format:
   - Use double line breaks between thoughts
   - Each 1-2 sentences should be in separate paragraphs
   - Include project hashtags and mentions naturally
   - Use proper cashtags for assets (like $BTC, $ETH)

4. Content:
   - Base your tweet strictly on the provided context
   - Do not make up or assume information
   - Focus on tech, innovation, and development
   - Avoid price predictions or financial advice

Previous tweets for reference (avoid repeating):
{my_tweets}

Recent project updates:
{project_tweets}

Generate a unique tweet that differs from previous ones in approach and style."""

PROMPT_FOR_QUOTED_TWEET = """ DONT USE HASHTAG You are autonomous AI Twitter Ambassador and crypto enthusiast with a vision for decentralized tech.

YOUR TASK IS TO COMMENT THIS TWEET: {tweet_for_quote}

The tweet should be bullish, positive, with humor.
You can add sarcasm if it's appropriate, and include memes if relevant.
The tweet should be written in simple, human language.
Use double line breaks as much as possible.
Every 1-2 sentences must be in different paragraphs separated by '\\n\\n'.

When referencing the project:
- Use the project tags found in the knowledge base
- If mentioning usernames, use @ symbol (example: @username)
When providing a reply, write the text directly, without prefixes or similar.

DO NOT USE EMOJIS

The new tweet should be different from my previous tweets, with a different idea, approach, and style.
Previous tweets for reference: {my_tweets}"""

PROMPT_FOR_NEWS_TWEET = """ DONT USE HASHTAG You are a Twitter content creator focused on technology and innovation. Your task is to analyze tweets and create engaging content that aligns with our knowledge base.
You need to create one twitter post.
You are an autonomous AI Twitter Ambassador for the project NFINITY. Your role is to enhance the brand presence of the project as a passionate and engaged community member, not as an official team representative.
You love this project, believe in its vision, and will do everything in your power to support it.

Analyze these tweets and themes:
{news_tweets}

Content Guidelines:
1. Tweet Format:
  - Write in English
  - Focus on AI, blockchain, and Web3 developments
  - Stay within 260 characters
  - Do not use emojis
  - Use hashtags found in our knowledge base when relevant

2. Content Rules:
  - Create original, meaningful insights
  - Keep a positive and engaging tone
  - Draw from the provided tweets and knowledge base
  - Do not mention sources or include links
  - Avoid specific dates or time references

3. Topic Boundaries:
  - Focus on technology and innovation
  - Avoid politics, controversy, or sensitive issues
  - Stay away from speculation or unverified claims
  - Use humor only when it fits naturally

4. Style Reference:
  Previous tweets to differentiate from:
  {my_tweets}

Create a unique tweet that builds on the news while staying aligned with our project's focus and knowledge base."""


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
""",
        },
        {"role": "user", "content": text},
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
    print(f"Tweet validating 2 {text}")
    return text


async def format_text(text: str) -> str:
    text = await add_blank_lines(text)

    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    for _ in range(20):
        if len(text) <= 280:
            return text
        messages = [
            {
                "role": "system",
                "content": "You are a text shortener. Your task is to reduce the text length, keeping "
                "its meaning and style unchanged. You can remove some sentences as long as it "
                "doesn't harm the overall meaning of the text. Also remove emojis. REMOVE HASHTAGS",
            },
            {"role": "user", "content": text},
        ]

        system_prompt = (
            "You are a text shortener. Your task is to reduce the text length, keeping "
            "its meaning and style unchanged. You can remove some sentences as long as it "
            "doesn't harm the overall meaning of the text. Also remove emojis. REMOVE HASHTAGS\n\n"
            f"{text}"
        )
        text = await send_openai_request(messages=messages, temperature=1.0)

        print(f"Tweet validating 1 {text}")
        text = await add_blank_lines(text)

        text = re.sub(r"#\w+", "", text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

    raise ValueError("Generated text is too long")


async def _handle_quote_tweet(
    project_tweet: Tweet, my_tweets: list[Post], username: str, keywords: list[str], themes: list[str]
) -> Post:
    """Tweet about project with quote project tweet"""
    tweet_text = await _create_quoted_tweet(
        tweet_for_quote=project_tweet.full_text,
        my_tweets=[tweet.text for tweet in my_tweets],
        keywords=keywords,
        themes=themes,
        username=username,
    )
    result = await create_post(
        access_token=await TwitterAuthClient.get_access_token(username),
        tweet_text=tweet_text,
        quote_tweet_id=project_tweet.id_str,
    )
    if result is None or "data" not in result or "id" not in result["data"]:
        print(f"create_post did not return the expected data: {result}")
        return None

    post = Post(
        id=result["data"]["id"],
        text=tweet_text,
        sender_username=username,
        quoted_tweet_id=project_tweet.id_str,
        timestamp=int(time.time()),
    )
    db.add_user_post(username, post)
    db.save_tweet_link("create_ambassador_tweet", result["data"]["id"])
    return post


async def _handle_regular_tweet(
    project_tweets: list[Tweet],
    my_tweets: list[Post],
    username: str,
    keywords: list[str],
    themes: list[str],
) -> Post | None:
    """Regular tweet about project"""
    print(f"Fetching tweet text for keyword: {keywords}, themes: {themes}")
    tweet_text = await _create_tweet(
        project_tweets=[tweet.full_text for tweet in project_tweets],
        my_tweets=[tweet.text for tweet in my_tweets],
        keywords=keywords,
        username=username,
        themes=themes,
    )

    print("Fetching access token for twitter")
    access_token = await TwitterAuthClient.get_access_token(username)
    print("Fetched access token successfully")

    print(f"Trying to create a post with tweet text: {tweet_text}")
    result = await create_post(
        access_token=access_token,
        tweet_text=tweet_text,
    )
    if result is None or "data" not in result or "id" not in result["data"]:
        print(f"create_post did not return the expected data: {result}")
        return None

    post = Post(id=result["data"]["id"], text=tweet_text, sender_username=username, timestamp=int(time.time()))
    print("Storing user post to DB")
    db.add_user_post(username, post)
    db.save_tweet_link("create_ambassador_tweet", result["data"]["id"])
    return post


async def _handle_news_tweet(my_tweets: list[Post], username: str, keywords: list[str], themes: list[str]) -> Post:
    """Tweet about news using project context"""
    all_news_tweets = []

    # Обрабатываем ключевые слова
    for keyword in keywords:
        try:
            # Создаем простой запрос для каждого ключевого слова
            simple_query = f"{keyword} lang:en -is:retweet"
            news = await search_tweets(query=simple_query)

            # Фильтруем результаты после получения
            filtered_news = [
                tweet
                for tweet in news
                if tweet.favorite_count >= 100
                and tweet.in_reply_to_status_id_str is None
                and len(tweet.full_text) > 200
            ]

            all_news_tweets.extend(
                tweet.full_text for tweet in filtered_news[:2]
            )  # Берем только 2 твита для каждого запроса
        except Exception as e:
            print(f"Error searching for news with keyword {keyword}: {e}")
            continue

    # Обрабатываем темы (хэштеги)
    for theme in themes:
        try:
            # Создаем простой запрос для каждой темы
            simple_query = f"#{theme} lang:en -is:retweet"
            news = await search_tweets(query=simple_query)

            # Фильтруем результаты после получения
            filtered_news = [
                tweet
                for tweet in news
                if tweet.favorite_count >= 100
                and tweet.in_reply_to_status_id_str is None
                and len(tweet.full_text) > 200
            ]

            all_news_tweets.extend(
                tweet.full_text for tweet in filtered_news[:2]
            )  # Берем только 2 твита для каждого запроса
        except Exception as e:
            print(f"Error searching for news with theme #{theme}: {e}")
            continue

    # Если не нашли новостей, вернем None
    if not all_news_tweets:
        print("No news tweets found")
        return None

    tweet_text = await _create_news_tweet(
        my_tweets=[tweet.text for tweet in my_tweets],
        news_tweets=all_news_tweets,
        keywords=keywords,
        username=username,
        themes=themes,
    )

    result = await create_post(
        access_token=await TwitterAuthClient.get_access_token(username),
        tweet_text=tweet_text,
    )
    if result is None or "data" not in result or "id" not in result["data"]:
        print(f"create_post did not return the expected data: {result}")
        return None

    post = Post(
        id=result["data"]["id"],
        text=tweet_text,
        sender_username=username,
        timestamp=int(time.time()),
        is_news_summary_tweet=True,
    )
    db.add_user_post(username, post)
    db.save_tweet_link("create_ambassador_tweet", result["data"]["id"])
    return post


async def _create_tweet(
    project_tweets: list[str],
    my_tweets: list[str],
    keywords: list[str],
    themes: list[str],
    username: str,
    prompt: str = PROMPT_FOR_TWEET,
) -> str:
    print("generate tweet")
    formatted_prompt = prompt.format(project_tweets=str(project_tweets), my_tweets=str(my_tweets))
    messages = [
        {"role": "system", "content": formatted_prompt},
    ]
    result = await send_openai_request(messages=messages, temperature=1.0)
    print(f"Created prompt: {prompt=}")
    return await format_text(result)


async def _create_quoted_tweet(
    tweet_for_quote: str,
    my_tweets: list[str],
    keywords: list[str],
    themes: list[str],
    username: str,
    prompt: str = PROMPT_FOR_QUOTED_TWEET,
) -> str:
    print(f"generate quote tweet: {tweet_for_quote=}")
    formatted_prompt = prompt.format(tweet_for_quote=tweet_for_quote, my_tweets=str(my_tweets))
    messages = [
        {"role": "system", "content": formatted_prompt},
    ]
    result = await send_openai_request(messages=messages, temperature=1.0)
    print(f"Created prompt: {prompt=}")
    return await format_text(result)


async def _create_news_tweet(
    news_tweets: list[str],
    my_tweets: list[str],
    keywords: list[str],
    themes: list[str],
    username: str,
    prompt: str = PROMPT_FOR_NEWS_TWEET,
) -> str:
    print(f"_create_news_tweet: {news_tweets=}")
    formatted_prompt = prompt.format(news_tweets=str(news_tweets), my_tweets=str(my_tweets))
    messages = [
        {"role": "system", "content": formatted_prompt},
    ]
    result = await send_openai_request(messages=messages, temperature=1.0)
    print(f"Created prompt: {prompt=}")
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
