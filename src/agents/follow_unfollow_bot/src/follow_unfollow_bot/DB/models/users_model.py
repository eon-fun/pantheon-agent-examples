from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import BigInteger, Column, ForeignKey, Integer, TIMESTAMP, Text
from sqlalchemy.orm import relationship

from DB.sqlalchemy_database_manager import Base


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
