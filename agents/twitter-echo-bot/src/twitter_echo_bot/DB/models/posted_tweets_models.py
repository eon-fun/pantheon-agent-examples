from datetime import datetime

from pydantic import Field
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from twitter_echo_bot.DB.models.base import BaseConfigModel
from twitter_echo_bot.DB.sqlalchemy_database_manager import Base


class AlchemyPostedTweet(Base):
    """История запощенных ботом твитов."""

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
    """История запощенных твитов."""

    id: int
    user_id: int
    source_tweet_id: str | None
    source_account_id: int | None
    is_send: bool
    posted_text: str
    posted_at: datetime = Field(default_factory=datetime.utcnow)
