from datetime import datetime
from typing import ClassVar

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlmodel import Column, Field, Integer, SQLModel


class RugCheckData(SQLModel, table=True):
    __tablename__ = "rug_check_data"

    id: int = Field(sa_column=Column(Integer, primary_key=True))
    base_coin_id: int = Field(foreign_key="base_coin.id")
    data: dict = Field(sa_column=Column(JSONB, nullable=True), default={})
    updated_at: datetime = Field(default_factory=datetime.now)

    base_coin: ClassVar = relationship("BaseCoin", back_populates="rug_check_data")
