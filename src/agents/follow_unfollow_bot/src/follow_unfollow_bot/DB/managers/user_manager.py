from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from DB.managers.base import BaseAlchemyManager
from DB.models import AlchemyUser
from DB.models.users_model import PGUserModel


class AlchemyUsersManager(BaseAlchemyManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_user(self, user_id: int,username) -> PGUserModel:
        """Создаёт запись пользователя"""
        user = AlchemyUser(id=user_id, followers_today=0,username=username)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return PGUserModel.from_orm(user)

    async def increment_followers(self, user_id: int):
        """Увеличивает followers_today на 1"""
        query = select(AlchemyUser).where(AlchemyUser.id == user_id)
        result = await self.session.execute(query)
        try:
            user = result.scalar_one()
            user.followers_today = (user.followers_today or 0) + 1
            await self.session.commit()
        except NoResultFound:
            print(f"Пользователь {user_id} не найден")

    async def get_user(self, user_id: int) -> Optional[PGUserModel]:
        """Получает пользователя по ID, если он существует"""
        query = select(AlchemyUser).where(AlchemyUser.id == user_id)
        result = await self.session.execute(query)
        user= result.scalar_one_or_none()
        return  PGUserModel.from_orm(user)

    async def delete_user(self, user_id: int):
        """Удаляет пользователя по ID"""
        query = select(AlchemyUser).where(AlchemyUser.id == user_id)
        result = await self.session.execute(query)
        user = result.scalar_one()
        await self.session.delete(user)
        await self.session.commit()
        return PGUserModel.from_orm(user)


    async def get_all_users(self)->List[PGUserModel]:
        query = select(AlchemyUser)
        result = await self.session.execute(query)
        users = result.scalars().all()
        return [PGUserModel.from_orm(user) for user in users]

    async def reset_followers_today(self,):
        """Обнуление подписок за сегодня у всех пользователей"""

        await self.session.execute(
            update(AlchemyUser).values(followers_today=0)
        )
        await self.session.commit()