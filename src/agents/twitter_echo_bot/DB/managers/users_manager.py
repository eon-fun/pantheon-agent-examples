from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from DB.managers.base import BaseAlchemyManager
from DB.models.users_models import AlchemyUser, PGUser


class AlchemyUsersManager(BaseAlchemyManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_filtered_users(self,):
        result = await self.session.execute(
            select(AlchemyUser)
            .where(AlchemyUser.persona_descriptor.isnot(None))
            .where(AlchemyUser.prompt.is_(None))
        )
        result = result.scalars().all()
        return [PGUser.from_orm(result) for result in result]

    async def add_prompt_to_user(self, user_id: int, prompt: str):
        """
        Добавляет или обновляет prompt для пользователя с указанным user_id.
        """

        result = await self.session.execute(select(AlchemyUser).where(AlchemyUser.id == user_id))
        user = result.scalars().one()
        user.prompt = prompt
        await self.session.commit()
        return user

    async def get_user_by_id(self, user_id: int)->PGUser:
        result = await self.session.execute(select(AlchemyUser).where(AlchemyUser.id == user_id))
        user = result.scalars().one()
        return PGUser.from_orm(user)

    async def create_user(self, user_data: PGUser) -> PGUser:
        new_user = AlchemyUser(**user_data.dict())
        self.session.add(new_user)
        await self.session.commit()
        return PGUser.from_orm(new_user)

    async def update_user(self, user_data: PGUser) -> PGUser:
        result = await self.session.execute(select(AlchemyUser).where(AlchemyUser.id == user_data.id))
        user = result.scalars().one()

        # Обновляем данные вручную
        for key, value in vars(user_data).items():
            if value is not None:
                setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)  # Обновляем объект из БД

        return PGUser.from_orm(user)