from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")  # Тип модели для аннотаций


class BaseAlchemyManager:
    def __init__(self, session: AsyncSession):
        self.session = session
