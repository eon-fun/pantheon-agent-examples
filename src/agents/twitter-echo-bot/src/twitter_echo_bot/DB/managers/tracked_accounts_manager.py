from typing import List

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from DB.managers.base import BaseAlchemyManager
from DB.models.tracked_accounts_models import PGTrackedAccount, AlchemyTrackedAccount


class AlchemyTrackedAccountsManager(BaseAlchemyManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_all_tracked_accounts(self,) -> List[PGTrackedAccount]:
        """
        Получает все отслеживаемые аккаунты Twitter.

        :param session: Асинхронная сессия SQLAlchemy.
        :return: Список объектов AlchemyTrackedAccount.
        """
        result = await self.session.execute(select(AlchemyTrackedAccount))
        results = result.scalars().all()
        return [PGTrackedAccount.from_orm(result) for result in results]

    async def add_tracked_accounts(self, user_id: int, twitter_handles: list[str]):
        # Получаем уже существующие аккаунты
        existing_query = text("""
            SELECT twitter_handle FROM tracked_accounts
            WHERE twitter_handle = ANY(:twitter_handles)
        """)
        result = await self.session.execute(existing_query, {"twitter_handles": twitter_handles})
        existing_accounts = {row[0] for row in
                             result.fetchall()}  # row.twitter_handle не всегда работает, поэтому row[0]

        # Определяем, какие хэндлы ещё не записаны в БД
        new_handles = [handle for handle in twitter_handles if handle not in existing_accounts]

        # Вставляем новые записи в tracked_accounts
        if new_handles:
            insert_query = text("""
                INSERT INTO tracked_accounts (twitter_handle)
                VALUES (:twitter_handle)
                ON CONFLICT (twitter_handle) DO NOTHING;
            """)
            await self.session.execute(
                insert_query, [{"twitter_handle": handle} for handle in new_handles]
            )
            await self.session.commit()  # Фиксируем вставку, иначе не увидим новые записи

        # Добавляем связи в user_tracked_accounts
        insert_links_query = text("""
            INSERT INTO user_tracked_accounts (user_id, twitter_handle)
            VALUES (:user_id, :twitter_handle)
            ON CONFLICT DO NOTHING;
        """)
        await self.session.execute(
            insert_links_query,
            [{"user_id": user_id, "twitter_handle": handle} for handle in twitter_handles]
        )

        await self.session.commit()
