from datetime import datetime
from typing import ClassVar

from sqlalchemy.orm import relationship
from sqlmodel import Column, Field, Integer, SQLModel, String


class BaseCoin(SQLModel, table=True):
    __tablename__ = "base_coin"

    id: int = Field(sa_column=Column(Integer, primary_key=True))
    token_address: str = Field(sa_column=Column(String(255), nullable=False, unique=True))
    creation_time: datetime = Field(default_factory=datetime.now)
    is_posted: bool = Field(default=False)

    dex_tools_data: ClassVar = relationship("DexToolsData", back_populates="base_coin", lazy="joined")
    rug_check_data: ClassVar = relationship("RugCheckData", back_populates="base_coin", lazy="joined")
