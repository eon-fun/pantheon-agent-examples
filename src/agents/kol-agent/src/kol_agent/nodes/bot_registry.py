from typing import List, Dict, Any
import random
import math
import logging
from kol_agent.models.raid_state import RaidState, BotsModel
from kol_agent.config import get_config
from redis_client.main import get_redis_db


from tweetscout_utils.main import get_tweet_by_link
from twitter_ambassador_utils.main import TwitterAuthClient

# Bot roles
BOT_ROLES = [
    "advocate",    # Advocate
    "skeptic",     # Skeptic
    "expert",      # Expert
    "enthusiast",  # Enthusiast
    "newbie"       # Newbie
]

ACTIONS = [
    "twitter_like",
    "twitter_comment",
    "twitter_retweet"
]

def update_bot_actions(bots: List[BotsModel], 
                       raid_minutes: float, 
                       type_of_action: str, 
                       bots_actions: List[Dict[str, Any]]):
    """
    Updates actions for the bots
    """
    for bot in bots:
        delay = random.uniform(1, raid_minutes*60)
        bots_actions.append({
            "type": type_of_action,
            "username": bot.username,
            "role": bot.role,
            "account_access_token": bot.account_access_token,
            "user_id": bot.user_id,
            "delay": delay,
            "content": None
        })

def plan_raid_actions(bots: List[BotsModel], raid_minutes: float):
    """
    Plans actions for the raid

    Args:
        state (RaidState): Current state
    """

    like_count = len(bots)
    comment_count = len(bots)
    retweet_count = len(bots)

    bots_actions = []

    for action in ACTIONS:
        update_bot_actions(bots, raid_minutes, action, bots_actions)


    message = f"Planned actions for the raid: {like_count} likes, {comment_count} comments, {retweet_count} retweets"

    return bots_actions, message


async def bot_registry(state: RaidState):
    """
    LangGraph node for bot management

    Args:
        state (OrionState): Current state

    Returns:
        RaidState: Updated state
    """


    updated_state = {}
    updated_state["tweet_content"] = state.get("tweet_content", "")

    updated_state["messages"] = state.get("messages", [])

    bots_actions, message = plan_raid_actions(
        state["bot_accounts"], state["raid_minutes"])
    updated_state["bots_actions"] = bots_actions

    # Add message to log
    updated_state["messages"].append({
        "type": "bot_assignment",
        "content": message
    })

    return updated_state
