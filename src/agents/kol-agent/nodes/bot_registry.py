from models.raid_state import RaidState
from typing import List, Dict, Any
import random
from constants import LIKE_PERCENTAGE, COMMENT_PERCENTAGE, REPLY_PERCENTAGE, RETWEET_PERCENTAGE
from api.twitter import get_tweet
from nodes.content_generator import generate_content_by_role
# Bot roles
BOT_ROLES = [
    "advocate",    # Advocate
    "skeptic",     # Skeptic
    "expert",      # Expert
    "enthusiast",  # Enthusiast
    "newbie"       # Newbie
]


def get_available_bots(count: int) -> List[Dict[str, Any]]:
    """
    Returns a list of available bots

    Returns:
        List[Dict[str, Any]]: List of bots
    """
    # In a real application, there would be a request to the DB or API here
    # Here we create mock bots for testing

    # Create "count" bots with different roles and styles
    bots = []
    for i in range(count):
        bot_id = f"bot_{i+1}"
        role = random.choice(BOT_ROLES)

        # Create a bot persona
        bot = {
            "id": bot_id,
            "role": role
        }

        bots.append(bot)

    return bots


def plan_raid_actions(bots: List[Dict[str, Any]], delay_minutes: float):
    """
    Plans actions for the raid

    Args:
        state (RaidState): Current state
    """
    import math
    like_count = math.ceil(len(bots) * LIKE_PERCENTAGE)
    comment_count = math.ceil(len(bots) * COMMENT_PERCENTAGE)
    reply_count = math.ceil(len(bots) * REPLY_PERCENTAGE)
    retweet_count = math.ceil(len(bots) * RETWEET_PERCENTAGE)

    actions = []
    for bot in bots[:like_count]:
        delay = random.uniform(1, delay_minutes*60)
        actions.append({
            "type": "twitter_like",
            "bot_id": bot["id"],
            "role": bot["role"],
            "delay": delay,
            "content": None
        })

    for bot in bots[:comment_count]:
        delay = random.uniform(1, delay_minutes*60)
        actions.append({
            "type": "twitter_comment",
            "bot_id": bot["id"],
            "role": bot["role"],
            "delay": delay,
            "content": None
        })

    # Shuffle bots for random distribution
    random.shuffle(bots)

    for bot in bots[:retweet_count]:
        delay = random.uniform(1, delay_minutes*60)
        actions.append({
            "type": "twitter_retweet",
            "bot_id": bot["id"],
            "role": bot["role"],
            "delay": delay,
            "content": None
        })

    message = f"Planned actions for the raid: {like_count} likes, {comment_count} comments, {reply_count} replies"

    return actions, message


def bot_registry(state: RaidState):
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
    selected_bots = get_available_bots(bot_count)

    # Update state depending on the task type
    # updated_state = state.copy()
    updated_state = {}
    updated_state["tweet_content"] = get_tweet(state["target_tweet_id"])["content"]
    updated_state["messages"] = state.get("messages", [])

    bots_actions, message = plan_raid_actions(
        selected_bots, state["delay_minutes"])
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
