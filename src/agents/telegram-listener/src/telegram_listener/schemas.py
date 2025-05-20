from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TelegramUser(BaseModel):
    id: int
    is_bot: bool
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None


class TelegramMessageData(BaseModel):
    message_id: int
    chat_id: int
    sender: TelegramUser
    text: Optional[str] = None
    timestamp: datetime
    raw_message: Dict[str, Any]


class StoredMessage(BaseModel):
    id: int = Field(description="Primary key in PostgreSQL, auto-incrementing")
    message_id: int
    chat_id: int
    user_id: int
    username: Optional[str] = None
    text: Optional[str] = None
    message_timestamp: datetime
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    embedding_model: Optional[str] = None


class QdrantPayload(BaseModel):
    text: Optional[str] = None
    chat_id: int
    user_id: int
    username: Optional[str] = None
    message_timestamp: datetime
