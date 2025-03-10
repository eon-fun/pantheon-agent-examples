




from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import BigInteger, Column, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.orm import relationship

from DB.sqlalchemy_database_manager import Base


class AlchemyTrackedAccount(Base):
    __tablename__ = "tracked_accounts"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("AlchemyUser", back_populates="tracked_accounts")




class PGTrackedAccount(BaseModel):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
