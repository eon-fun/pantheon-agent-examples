from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TelegramUser(BaseModel):
    id: int
    is_bot: bool
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


class TelegramMessageData(BaseModel):
    message_id: int
    chat_id: int
    sender: TelegramUser
    text: str | None = None
    timestamp: datetime
    raw_message: dict[str, Any]


class StoredMessage(BaseModel):
    id: int = Field(description="Primary key in PostgreSQL, auto-incrementing")
    message_id: int
    chat_id: int
    user_id: int
    username: str | None = None
    text: str | None = None
    message_timestamp: datetime
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    embedding_model: str | None = None


class QdrantPayload(BaseModel):
    text: str | None = None
    chat_id: int
    user_id: int
    username: str | None = None
    message_timestamp: datetime
