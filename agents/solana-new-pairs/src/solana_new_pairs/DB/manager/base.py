from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, text, insert
from typing import Optional, Type, List, TypeVar


ModelType = TypeVar("ModelType")  # Тип модели для аннотаций


class BaseAlchemyManager:
    def __init__(self, session: AsyncSession):
        self.session = session

