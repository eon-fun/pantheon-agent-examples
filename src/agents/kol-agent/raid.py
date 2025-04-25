import random
from typing import Literal, Optional, List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from nodes.bot_registry import bot_registry
# from nodes.content_generator import content_generator
# from nodes.twitter_api_handler import twitter_api_handler
from models.raid_state import RaidState
from langgraph.constants import Send
from nodes.twitter_api_handler import twitter_like, twitter_comment, twitter_retweet


def continue_to_twitter(state: RaidState):
    return [Send(
        action["type"],
        {
            "action": action,
            "target_tweet_id": state["target_tweet_id"],
            "tweet_content": state["tweet_content"]
        }
    ) for action in state["bots_actions"]]


workflow = StateGraph(RaidState)
# Add nodes
workflow.add_node("bot_registry", bot_registry)
# workflow.add_node("content_generator", content_generator)
workflow.add_node("twitter_like", twitter_like)
workflow.add_node("twitter_comment", twitter_comment)
workflow.add_node("twitter_retweet", twitter_retweet)

# Initial flow: planning -> bot selection
workflow.add_edge(START, "bot_registry")

# From bot selection to action planner
workflow.add_conditional_edges("bot_registry", continue_to_twitter, [
                               "twitter_like", "twitter_comment", "twitter_retweet"])

# From Twitter API handler to action planner
workflow.add_edge("twitter_like", END)
workflow.add_edge("twitter_comment", END)
workflow.add_edge("twitter_retweet", END)

# Compile the graph
graph = workflow.compile()
