from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator
from pydantic import BaseModel


class Action(BaseModel):
    type: str
    bot_id: str
    role: str
    delay: float
    content: str

class ExecutedAction(BaseModel):
    action: Action
    status: str
    created_at: float
class RaidState(TypedDict):
    # Task parameters
    target_tweet_id: str
    bot_count: int
    raid_minutes: float

    # Raid state
    bots_actions: Optional[List[Action]]  # list of bots with tasks
    executed_actions: Annotated[List[ExecutedAction], operator.add]  # executed actions
    tweet_content: Optional[str]

    # Metadata
    messages: Optional[List[Dict[str, Any]]]  # message/action history


class TwitterState(TypedDict):
    action: Action
    target_tweet_id: str
