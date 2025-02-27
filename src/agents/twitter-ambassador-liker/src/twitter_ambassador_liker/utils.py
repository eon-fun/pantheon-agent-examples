import sys
from importlib.metadata import EntryPoint, entry_points
from twitter_ambassador_tweetscout_requests.main import search_tweets, Tweet
from typing import Sequence


def get_entry_points(group: str) -> list[EntryPoint]:
    if sys.version_info >= (3, 10):
        entrypoints = entry_points(group=group)

    entrypoints = entry_points()
    try:
        return entrypoints.get(group, [])
    except AttributeError:
        return entrypoints.select(group=group)


def get_entrypoint(group_name: str, target_entrypoint: str = "target", default_entrypoint: str = "basic") -> EntryPoint:
    entrypoints = get_entry_points(group_name)
    try:
        return entrypoints[target_entrypoint]
    except KeyError:
        return entrypoints[default_entrypoint]



def default_stringify_rule_for_arguments(args):
    if len(args) == 1:
        return str(args[0])
    else:
        return str(tuple(args))


async def _get_tweets() -> Sequence[Tweet]:
    tweets_dict = {}
    search_terms = [
        "NFINITY AI Web3",
        "AI-driven crypto",
        "AI agent web3",
        "decentralized marketplaces AI",
    ]
    for search_term in search_terms:
        result = await search_tweets(f"{search_term} -filter:replies min_faves:20 lang:en")
        for tweet in result[:2]:
            if tweet.id_str not in tweets_dict:
                tweets_dict[tweet.id_str] = tweet

    return list(tweets_dict.values())
