from kol_agent.models.raid_state import RaidState
from kol_agent.nodes.bot_registry import ACTIONS, bot_registry
from kol_agent.nodes.twitter_api_handler import twitter_comment, twitter_like, twitter_retweet
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph


def continue_to_twitter(state: RaidState):
    return [
        Send(
            action["type"],
            {"action": action, "target_tweet_id": state["target_tweet_id"], "tweet_content": state["tweet_content"]},
        )
        for action in state["bots_actions"]
    ]


def get_raid_workflow() -> StateGraph:
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
    workflow.add_conditional_edges("bot_registry", continue_to_twitter, ACTIONS)

    # From Twitter API handler to action planner
    workflow.add_edge("twitter_like", END)
    workflow.add_edge("twitter_comment", END)
    workflow.add_edge("twitter_retweet", END)

    return workflow
