from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from DB.models.base import BaseConfigModel
from DB.sqlalchemy_database_manager import Base
class AlchemyPostedTweet(Base):
    """
    История запощенных ботом твитов.
    """
    __tablename__ = "posted_tweets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_tweet_id = Column(String(255), ForeignKey("tweets_history.tweet_id", ondelete="SET NULL"))
    source_account_id = Column(Integer, ForeignKey("tracked_accounts.id", ondelete="SET NULL"))
    is_send = Column(Boolean, default=False)
    posted_text = Column(Text, nullable=False)
    posted_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("AlchemyUser", back_populates="posted_tweets")
    source_account = relationship("AlchemyTrackedAccount", back_populates="posted_tweets")

class PGPostedTweet(BaseConfigModel):
    """
    История запощенных твитов.
    """
    id: int
    user_id: int
    source_tweet_id: Optional[str]
    source_account_id: Optional[int]
    is_send: bool
    posted_text: str
    posted_at: datetime = Field(default_factory=datetime.utcnow)
