from datetime import datetime

from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from twitter_echo_bot.DB.models.base import BaseConfigModel
from twitter_echo_bot.DB.sqlalchemy_database_manager import Base


class AlchemyUserTweetMatch(Base):
    __tablename__ = "user_tweet_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tweet_id = Column(String(255), ForeignKey("tweets_history.tweet_id", ondelete="CASCADE"), nullable=False)
    is_processed = Column(Boolean, default=False, nullable=False)
    matched_at = Column(TIMESTAMP, server_default=func.now())

    # Связи
    user = relationship("AlchemyUser", back_populates="tweet_matches")
    tweet = relationship("AlchemyTweetHistory", back_populates="user_matches")


class PGUserTweetMatch(BaseConfigModel):
    id: int
    user_id: int
    tweet_id: str
    is_processed: bool
    matched_at: datetime

    class Config:
        from_attributes = True  # Для работы с ORM-моделями
