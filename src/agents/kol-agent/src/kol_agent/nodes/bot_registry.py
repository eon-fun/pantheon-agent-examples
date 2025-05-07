from typing import List, Dict, Any
import random
import math
import logging
from kol_agent.models.raid_state import RaidState
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

async def get_twitter_credentials(account: str):
    """
    Gets the twitter credentials
    """
    account_access_token = await TwitterAuthClient.get_access_token(account)
    user_id = TwitterAuthClient.get_static_data(account)['id']
    return {
        "account_access_token": account_access_token,
        "user_id": user_id
    }


async def get_available_bots(count: int) -> List[Dict[str, Any]]:
    """
    Returns a list of available bots

    Returns:
        List[Dict[str, Any]]: List of bots
    """
    # In a real application, there would be a request to the DB or API here
    # Here we create mock bots for testing

    # Create "count" bots with different roles and styles
    bots = []
    db = get_redis_db()
    accounts = db.get_active_twitter_accounts()
    if len(accounts) > count:
        accounts = random.sample(accounts, count)
    for account in accounts:
        # Create a bot persona
        try:
            credentials = await get_twitter_credentials(account)
        except Exception as e:
            logging.error(f"Error getting twitter credentials: {e}")
            continue
        bot = {
            "id": account,
            "role": random.choice(BOT_ROLES),
            "account_access_token": credentials["account_access_token"],
            "user_id": credentials["user_id"]
        }

        bots.append(bot)

    return bots

def update_bot_actions(bots: List[Dict[str, Any]], 
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
            "bot_id": bot["id"],
            "role": bot["role"],
            "account_access_token": bot["account_access_token"],
            "user_id": bot["user_id"],
            "delay": delay,
            "content": None
        })

def plan_raid_actions(bots: List[Dict[str, Any]], raid_minutes: float):
    """
    Plans actions for the raid

    Args:
        state (RaidState): Current state
    """

    config = get_config()
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
    # Determine the number of bots
    bot_count = state["bot_count"]

    # Select bots for the task
    selected_bots = await get_available_bots(bot_count)

    # Update state depending on the task type
    # updated_state = state.copy()
    updated_state = {}
    tweet_id = state["target_tweet_id"]
    user = state["target_user"]
    link = f"https://x.com/{user}/status/{tweet_id}"
    tweet = await get_tweet_by_link(link)
    updated_state["tweet_content"] = tweet.full_text

    updated_state["messages"] = state.get("messages", [])

    bots_actions, message = plan_raid_actions(
        selected_bots, state["raid_minutes"])
    updated_state["bots_actions"] = bots_actions

    # Add message to log
    updated_state["messages"].append({
        "type": "bot_assignment",
        "content": f"Selected {len(selected_bots)} bots for the raid"
    })
    updated_state["messages"].append({
        "type": "bot_assignment",
        "content": message
    })

    return updated_state
