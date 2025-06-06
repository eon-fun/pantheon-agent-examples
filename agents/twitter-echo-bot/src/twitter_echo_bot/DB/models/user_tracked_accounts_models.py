from datetime import datetime

from pydantic import Field
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from twitter_echo_bot.DB.models.base import BaseConfigModel
from twitter_echo_bot.DB.sqlalchemy_database_manager import Base


class AlchemyUserTrackedAccount(Base):
    """Связь пользователей с отслеживаемыми аккаунтами."""

    __tablename__ = "user_tracked_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    twitter_handle = Column(
        String(255), ForeignKey("tracked_accounts.twitter_handle", ondelete="CASCADE"), nullable=False
    )
    added_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("AlchemyUser", back_populates="tracked_accounts")
    tracked_account = relationship("AlchemyTrackedAccount", back_populates="users_tracking")


class PGUserTrackedAccount(BaseConfigModel):
    """Связь пользователя и отслеживаемого аккаунта."""

    id: int
    user_id: int
    twitter_handle: str
    added_at: datetime = Field(default_factory=datetime.utcnow)
