import time
from twitter_ambassador_utils.main import set_like, TwitterAuthClient, retweet, create_post
import logging

from kol_agent.models.raid_state import TwitterState, Action
# from kol_agent.api.twitter import post_comment, post_reply, like_tweet, retweet
from kol_agent.nodes.content_generator import generate_content_by_role

async def get_twitter_credentials(action: Action):
    """
    Gets the twitter credentials
    """
    account_access_token = await TwitterAuthClient.get_access_token(action["bot_id"])
    user_id = TwitterAuthClient.get_static_data(action["bot_id"])['id']
    return {
        "account_access_token": account_access_token,
        "user_id": user_id
    }

async def twitter_retweet(state: TwitterState) -> TwitterState:
    """
    Performs a retweet
    """
    time.sleep(state["action"]["delay"])
    status = True
    try:
        credentials = await get_twitter_credentials(state["action"])
        result = await retweet(
            token=credentials["account_access_token"],
            tweet_id=state["target_tweet_id"],
            user_id=credentials["user_id"]
        )
    except Exception as e:
        status = False
        result = e
        logging.error(f"Error liking tweet: {e}")
    executed_actions = {
            "success": status,
            "action": state["action"],
            "created_at": time.time(),
            "result": result
        }
    return {
        "executed_actions": [executed_actions]
    }


async def twitter_like(state: TwitterState) -> TwitterState:
    """
    Performs a like
    """
    time.sleep(state["action"]["delay"])
    status = True
    try:
        credentials = await get_twitter_credentials(state["action"])
        result = await set_like(
            token=credentials["account_access_token"],
            tweet_id=state["target_tweet_id"],
            user_id=credentials["user_id"]
        )
    except Exception as e:
        status = False
        result = e
        logging.error(f"Error liking tweet: {e}")
    
    executed_actions = {
            "success": status,
            "action": state["action"],
            "created_at": time.time(),
            "result": result
        }
    return {
        "executed_actions": [executed_actions]
    }


async def twitter_comment(state: TwitterState) -> TwitterState:
    """
    Performs a comment
    """
    content_comment = generate_content_by_role(
            state["action"]["role"], state["tweet_content"])
    time.sleep(state["action"]["delay"])
    status = True
    try:
        credentials = await get_twitter_credentials(state["action"])
        result = await create_post(
            access_token=credentials["account_access_token"],
            tweet_text=content_comment,
            commented_tweet_id=state["target_tweet_id"]
        )
    except Exception as e:
        status = False
        result = e
        logging.error(f"Error liking tweet: {e}")
    executed_actions = {
            "success": status,
            "action": state["action"],
            "created_at": time.time(),
            "result": result,
            "content_comment": content_comment
        }
    return {
        "executed_actions": [executed_actions]
    }


async def twitter_reply(state: TwitterState) -> TwitterState:
    """
    Performs a reply to a comment
    """
    content_reply = generate_content_by_role(
            state["action"]["role"], state["tweet_content"])
    time.sleep(state["action"]["delay"])
    status = True
    try:
        credentials = await get_twitter_credentials(state["action"])
        result = await create_post(
            access_token=credentials["account_access_token"],
            tweet_text=content_reply,
            commented_tweet_id=state["target_tweet_id"]
        )
    except Exception as e:
        status = False
        result = e
        logging.error(f"Error liking tweet: {e}")
    executed_actions = {
            "success": status,
            "action": state["action"],
            "created_at": time.time(),
            "result": result
        }
    return {
        "executed_actions": [executed_actions]
    }
