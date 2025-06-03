from datetime import datetime

from pydantic import Field
from sqlalchemy import TIMESTAMP, Column, Integer, String
from sqlalchemy.orm import relationship
from twitter_echo_bot.DB.models.base import BaseConfigModel
from twitter_echo_bot.DB.sqlalchemy_database_manager import Base


class AlchemyTrackedAccount(Base):
    """Аккаунты Twitter, которые отслеживаются."""

    __tablename__ = "tracked_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    twitter_handle = Column(String(255), unique=True, nullable=False)
    last_checked = Column(TIMESTAMP, default=datetime.utcnow)

    users_tracking = relationship("AlchemyUserTrackedAccount", back_populates="tracked_account")
    tweets_history = relationship("AlchemyTweetHistory", back_populates="account")
    posted_tweets = relationship("AlchemyPostedTweet", back_populates="source_account")


class PGTrackedAccount(BaseConfigModel):
    """Модель отслеживаемого аккаунта."""

    id: int
    twitter_handle: str
    last_checked: datetime = Field(default_factory=datetime.utcnow)
