import asyncio
import logging
import time

from kol_agent.models.raid_state import TwitterState
from kol_agent.nodes.content_generator import generate_content_by_role
from twitter_ambassador_utils.main import create_post, retweet, set_like


async def twitter_retweet(state: TwitterState) -> TwitterState:
    """Performs a retweet"""
    await asyncio.sleep(state["action"]["delay"])
    status = True
    try:
        result = await retweet(
            token=state["action"]["account_access_token"],
            tweet_id=state["target_tweet_id"],
            user_id=state["action"]["user_id"],
        )
    except Exception as e:
        status = False
        result = e
        logging.error(f"Error liking tweet: {e}")
    executed_actions = {
        "success": status,
        "action": state["action"],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "result": result,
    }
    return {"executed_actions": [executed_actions]}


async def twitter_like(state: TwitterState) -> TwitterState:
    """Performs a like"""
    await asyncio.sleep(state["action"]["delay"])
    status = True
    try:
        result = await set_like(
            token=state["action"]["account_access_token"],
            tweet_id=state["target_tweet_id"],
            user_id=state["action"]["user_id"],
        )
    except Exception as e:
        status = False
        result = e
        logging.error(f"Error liking tweet: {e}")

    executed_actions = {
        "success": status,
        "action": state["action"],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "result": result,
    }
    return {"executed_actions": [executed_actions]}


async def twitter_comment(state: TwitterState) -> TwitterState:
    """Performs a comment"""
    content_comment = generate_content_by_role(state["action"]["role"], state["tweet_content"])
    await asyncio.sleep(state["action"]["delay"])
    status = True
    try:
        result = await create_post(
            access_token=state["action"]["account_access_token"],
            tweet_text=content_comment,
            commented_tweet_id=state["target_tweet_id"],
        )
    except Exception as e:
        status = False
        result = e
        logging.error(f"Error liking tweet: {e}")
    executed_actions = {
        "success": status,
        "action": state["action"],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "result": result,
        "content_comment": content_comment,
    }
    return {"executed_actions": [executed_actions]}


async def twitter_reply(state: TwitterState) -> TwitterState:
    """Performs a reply to a comment"""
    content_reply = generate_content_by_role(state["action"]["role"], state["tweet_content"])
    await asyncio.sleep(state["action"]["delay"])
    status = True
    try:
        result = await create_post(
            access_token=state["action"]["account_access_token"],
            tweet_text=content_reply,
            commented_tweet_id=state["target_tweet_id"],
        )
    except Exception as e:
        status = False
        result = e
        logging.error(f"Error liking tweet: {e}")
    executed_actions = {
        "success": status,
        "action": state["action"],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "result": result,
    }
    return {"executed_actions": [executed_actions]}
