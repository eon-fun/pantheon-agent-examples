from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, text, insert
from typing import Optional, Type, List, TypeVar


from custom_logs.custom_logs import log

ModelType = TypeVar("ModelType")  # Тип модели для аннотаций


class BaseAlchemyManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_exists(
        self, model: Type[ModelType], id_field: str, id_value: int
    ) -> bool:
        """Проверить, существует ли объект с указанным ID"""
        stmt = select(model).where(getattr(model, id_field) == id_value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(self, model: Type[ModelType], **kwargs) -> ModelType:
        """Создать новую запись"""
        new_model = model(**kwargs)
        self.session.add(new_model)
        await self.session.commit()
        return new_model

    async def get_by_id(
        self, model: Type[ModelType], id_field: str, id_value: int
    ) -> Optional[ModelType]:
        """Получить объект по ID"""
        stmt = select(model).where(getattr(model, id_field) == id_value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, model: Type[ModelType]) -> List[ModelType]:
        """Получить все записи из таблицы"""
        stmt = select(model)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_by_id(
        self, model: Type[ModelType], id_field: str, id_value: int, **kwargs
    ) -> bool:
        """Обновить запись по ID"""
        stmt = (
            update(model)
            .where(getattr(model, id_field) == id_value)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def delete_by_id(
        self, model: Type[ModelType], id_field: str, id_value: int
    ) -> bool:
        """Удалить запись по ID"""
        stmt = delete(model).where(getattr(model, id_field) == id_value)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

