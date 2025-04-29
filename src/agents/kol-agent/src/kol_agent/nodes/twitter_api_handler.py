import time

from kol_agent.models.raid_state import TwitterState
from kol_agent.api.twitter import post_comment, post_reply, like_tweet, retweet
from kol_agent.nodes.content_generator import generate_content_by_role


def twitter_retweet(state: TwitterState) -> TwitterState:
    """
    Performs a retweet
    """
    time.sleep(state["action"]["delay"])
    return {
        "executed_actions": [
            retweet(state["action"])
        ]
    }


def twitter_like(state: TwitterState) -> TwitterState:
    """
    Performs a like
    """
    time.sleep(state["action"]["delay"])
    return {
        "executed_actions": [
            like_tweet(state["action"])
        ]
    }


def twitter_comment(state: TwitterState) -> TwitterState:
    """
    Performs a comment
    """
    content_comment = generate_content_by_role(
            state["action"]["role"], "comment", state["tweet_content"])
    time.sleep(state["action"]["delay"])
    return {
        "executed_actions": [
            post_comment(state["action"], content_comment)
        ]
    }


def twitter_reply(state: TwitterState) -> TwitterState:
    """
    Performs a reply to a comment
    """
    content_reply = generate_content_by_role(
            state["action"]["role"], "reply", state["tweet_content"])
    time.sleep(state["action"]["delay"])
    return {
        "executed_actions": [
            post_reply(state["action"], content_reply)
        ]
    }
