from datetime import datetime

from follow_unfollow_bot.DB.sqlalchemy_database_manager import Base
from pydantic import BaseModel
from sqlalchemy import TIMESTAMP, BigInteger, Column, Integer, Text
from sqlalchemy.orm import relationship


class AlchemyUser(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(Text, nullable=False)
    followers_today = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    tracked_accounts = relationship("AlchemyTrackedAccount", back_populates="user")


# Pydantic модели
class PGUserModel(BaseModel):
    id: int
    username: str
    followers_today: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True
