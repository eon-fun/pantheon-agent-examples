from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from DB.models.base import BaseConfigModel
from DB.sqlalchemy_database_manager import Base
class AlchemyTweetHistory(Base):
    """
    История твитов отслеживаемых аккаунтов.
    """
    __tablename__ = "tweets_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("tracked_accounts.id", ondelete="CASCADE"), nullable=False)
    tweet_id = Column(String(255), unique=True, nullable=False)
    tweet_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    fetched_at = Column(TIMESTAMP, default=datetime.utcnow)

    account = relationship("AlchemyTrackedAccount", back_populates="tweets_history")
    user_matches = relationship("AlchemyUserTweetMatch", back_populates="tweet", cascade="all, delete-orphan")


class PGTweetHistory(BaseConfigModel):
    """
    История твитов.
    """
    id: int
    account_id: int
    tweet_id: str
    tweet_text: str
    created_at: datetime
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

