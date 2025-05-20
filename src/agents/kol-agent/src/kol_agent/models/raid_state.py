import operator
from typing import Annotated, Any, TypedDict

from pydantic import BaseModel


class BotsModel(BaseModel):
    role: str
    account_access_token: str
    username: str
    user_id: str


class Action(BaseModel):
    type: str
    username: str
    role: str
    account_access_token: str
    user_id: str
    delay: float
    content: str


class ExecutedAction(BaseModel):
    action: Action
    status: str
    created_at: float


class RaidState(TypedDict):
    # Task parameters
    target_tweet_id: str
    tweet_content: str
    bot_accounts: list[BotsModel]
    raid_minutes: float

    # Raid state
    bots_actions: list[Action] | None  # list of bots with tasks
    executed_actions: Annotated[list[ExecutedAction], operator.add]  # executed actions

    # Metadata
    messages: list[dict[str, Any]] | None  # message/action history


class TwitterState(TypedDict):
    action: Action
    target_tweet_id: str
    tweet_content: str
