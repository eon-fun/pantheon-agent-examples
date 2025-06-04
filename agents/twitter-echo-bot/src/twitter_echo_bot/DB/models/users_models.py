from datetime import datetime

from pydantic import Field
from sqlalchemy import TIMESTAMP, BigInteger, Column, String, Text
from sqlalchemy.orm import relationship
from twitter_echo_bot.DB.models.base import BaseConfigModel
from twitter_echo_bot.DB.sqlalchemy_database_manager import Base


class AlchemyUser(Base):
    """Пользователи системы."""

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    persona_descriptor = Column(Text, nullable=True, default=None)
    prompt = Column(Text, nullable=True, default=None)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    tracked_accounts = relationship("AlchemyUserTrackedAccount", back_populates="user")
    posted_tweets = relationship("AlchemyPostedTweet", back_populates="user")
    tweet_matches = relationship("AlchemyUserTweetMatch", back_populates="user", cascade="all, delete-orphan")


class PGUser(BaseConfigModel):
    """Модель пользователя."""

    id: int
    username: str
    persona_descriptor: str | None = None
    prompt: str | None = None
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
