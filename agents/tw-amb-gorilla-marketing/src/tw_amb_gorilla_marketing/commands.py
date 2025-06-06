from collections.abc import Sequence

from send_openai_request.main import send_openai_request
from tweetscout_utils.main import Tweet, search_tweets

PROMPT_FOR_CHECK = """You are a technology and Web3 enthusiast focused on AI and blockchain innovations.

Your task is to analyze tweets and determine if they discuss topics related to our focus areas.
You should return True if the tweet provides an opportunity for engaging in a meaningful positive conversation.
Look for discussions about:
- AI and blockchain technology
- Web3 developments
- Decentralized systems
- Technology innovations

Do not engage with:
- Token prices or trading
- Project partnerships or collaborations
- Marketing or promotional content
- Non-technical discussions

Tweet to evaluate:
{tweet_text}

Respond with one word - True or False."""

PROMPT_FOR_COMMENT = """ DONT USE HASHTAG You are a technology enthusiast engaging in Web3 and AI discussions.
You need to create one comment for the twitter post.
You are an autonomous AI Twitter Ambassador for the project NFINITY. Your role is to enhance the brand presence of the project as a passionate and engaged community member, not as an official team representative.
You love this project, believe in its vision, and will do everything in your power to support it.

Your task is to write a very brief comment (1-2 sentences) in response to a tweet.
The comment should:
- Express relevant thoughts based on the knowledge context
- Use natural, human-like language
- Fit organically into the conversation
- Stay focused on technology and innovation

Guidelines:
- Keep it brief and meaningful
- No hashtags or emojis
- Base response on knowledge context
- Don't promote or advertise
- Be authentic and engaging

Tweet to respond to:
{tweet_text}"""


async def find_tweets_for_gorilla_marketing(access_token: str) -> Sequence[Tweet]:
    """Find relevant tweets for gorilla marketing campaign.
    Searches for tweets related to specific terms that have at least 5 likes,
    are in English, and aren't replies or from the nfinityAI account.

    Args:
        access_token: Twitter API token

    Returns:
        A list of unique tweets matching the search criteria

    """
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
        query = f"{search_term} min_retweets:5 lang:en -is:reply -from:nfinityAI"

        try:
            # Передаем access_token как обязательный параметр
            result = await search_tweets(access_token=access_token, query=query)

            # Берем до трех твитов из результатов
            for tweet in result[:3]:
                if tweet.id_str not in tweets_dict:
                    tweets_dict[tweet.id_str] = tweet

        except Exception as e:
            print(f"Error searching for '{search_term}': {e}")
            continue  # Продолжаем с другими поисковыми запросами, если один не удался

    return list(tweets_dict.values())


async def check_tweets_for_gorilla_marketing(
    tweets: Sequence[Tweet], keywords: list[str], themes: list[str], my_username: str, prompt: str = PROMPT_FOR_CHECK
) -> Sequence[Tweet]:
    good_tweets = []

    for tweet in tweets:
        formatted_prompt = prompt.format(tweet_text=tweet.full_text, keywords=keywords, themes=themes)

        messages = [{"role": "system", "content": formatted_prompt}]

        result = await send_openai_request(messages=messages, temperature=1.0)

        if "true" in result.lower():
            good_tweets.append(tweet)

    print(f"Count good tweets {len(good_tweets)=} {good_tweets}")
    return good_tweets


async def create_text_for_gorilla_marketing(
    tweet_text: str, keywords: list[str], themes: list[str], my_username: str, prompt: str = PROMPT_FOR_COMMENT
) -> str:
    formatted_prompt = prompt.format(tweet_text=tweet_text, keywords=keywords, themes=themes)

    messages = [{"role": "system", "content": formatted_prompt}]
    result = await send_openai_request(messages=messages, temperature=1.0)
    return result
