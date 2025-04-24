import random
from typing import Literal, Optional, List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from nodes.bot_registry import bot_registry
from nodes.content_generator import content_generator
from nodes.action_scheduler import action_scheduler
from nodes.twitter_api_handler import twitter_api_handler
from models.raid_state import RaidState


workflow = StateGraph(RaidState)
# Add nodes
workflow.add_node("bot_registry", bot_registry)
workflow.add_node("content_generator", content_generator)
workflow.add_node("action_scheduler", action_scheduler)
workflow.add_node("twitter_api_handler", twitter_api_handler)


# Set task_planner as the entry node
# workflow.set_entry_point("task_planner")

# Initial flow: planning -> bot selection
workflow.add_edge(START, "bot_registry")

# From bot selection to action scheduler
workflow.add_edge("bot_registry", "action_scheduler")

workflow.add_edge("action_scheduler", "content_generator")
# From action scheduler to content generator
workflow.add_edge("content_generator", "twitter_api_handler")

# From Twitter API handler to END
workflow.add_edge("twitter_api_handler", END)

# Compile the graph
graph = workflow.compile()
