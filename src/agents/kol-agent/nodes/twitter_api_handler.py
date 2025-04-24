import logging
from models.raid_state import RaidState
from api.twitter import post_comment, post_reply, like_tweet, retweet
from typing import Dict, Any


def execute_pending_action(action: Dict[str, Any], bot_id: str) -> Dict[str, Any]:
    """
    Executes a pending action via the Twitter API

    Args:
        action (Dict[str, Any]): Action description
        bot_id (str): Bot ID

    Returns:
        Dict[str, Any]: Action execution result
    """
    action_type = action["type"]
    tweet_id = action.get("tweet_id", action.get("target_id"))

    if action_type == "comment":
        content = action["content"]
        print(f"Bot {bot_id} posts a comment to tweet {tweet_id}")
        result = post_comment(tweet_id, content, bot_id)

    elif action_type == "reply":
        content = action["content"]
        print(
            f"Bot {bot_id} posts a reply to comment {tweet_id}")
        result = post_reply(tweet_id, content, bot_id)

    elif action_type == "like":
        print(f"Bot {bot_id} likes tweet {tweet_id}")
        result = like_tweet(tweet_id, bot_id)

    elif action_type == "retweet":
        print(f"Bot {bot_id} retweets {tweet_id}")
        result = retweet(tweet_id, bot_id)

    else:
        print(f"Unknown action type: {action_type}")
        result = {"status": "error",
                  "message": f"Unknown action type: {action_type}"}

    return result


def twitter_api_handler(state: RaidState) -> RaidState:
    """
    LangGraph node for interacting with the Twitter API

    Args:
        state (OrionState): Current state

    Returns:
        OrionState: Updated state
    """

    executed_actions = []
    for bot in state["assigned_bots"]:
        for action in bot["actions"]:                # Execute action
            result = execute_pending_action(action, bot["id"])
            executed_actions.append(result)
    return {"executed_actions": executed_actions}
