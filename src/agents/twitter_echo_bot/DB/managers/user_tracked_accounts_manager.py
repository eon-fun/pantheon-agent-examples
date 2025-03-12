
from sqlalchemy.ext.asyncio import AsyncSession

from DB.managers.base import BaseAlchemyManager


class AlchemyUsersTrackedAccountsManager(BaseAlchemyManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)