from follow_unfollow_bot.DB.managers.base import BaseAlchemyManager
from follow_unfollow_bot.DB.models import AlchemyTrackedAccount
from follow_unfollow_bot.DB.models.tracked_accounts_model import PGTrackedAccount
from sqlalchemy.ext.asyncio import AsyncSession


class AlchemyTrackedAccountsManager(BaseAlchemyManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def add_tracked_account(self, user_id: int, account_id: int) -> PGTrackedAccount:
        """Добавляет запись в tracked_accounts."""
        new_account = AlchemyTrackedAccount(id=account_id, user_id=user_id)

        self.session.add(new_account)
        await self.session.commit()
        return PGTrackedAccount.from_orm(new_account)
