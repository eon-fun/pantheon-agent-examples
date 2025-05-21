from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from solana_new_pairs.DB.manager.base import BaseAlchemyManager
from solana_new_pairs.DB.models.coin_model import BaseCoin
from datetime import datetime, timedelta

from solana_new_pairs.DB.models.rug_check_model import RugCheckData


class AlchemyBaseCoinManager(BaseAlchemyManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_base_coin(self, token_address: str) -> BaseCoin:
        """Создает новую запись в таблице BaseCoin или возвращает существующую"""
        new_coin = BaseCoin(token_address=token_address)

        self.session.add(new_coin)
        await self.session.commit()  # Записываем изменения в БД
        return new_coin

    async def get_base_coin_with_all_data(self, address: str):
        """Получение монеты со всеми связанными данными"""
        one_minute_ago = datetime.now() - timedelta(minutes=1)

        query = (
            select(BaseCoin)
            .where(BaseCoin.token_address == address)
            .options(
                joinedload(BaseCoin.dex_tools_data),
                joinedload(BaseCoin.rug_check_data.and_(RugCheckData.updated_at >= one_minute_ago))
            )
        )
        result = await self.session.execute(query)
        coin = result.scalars().first()
        return {
            "id": coin.id,
            "token_address": coin.token_address,
            "creation_time": coin.creation_time,
            "dex_tools_data": coin.dex_tools_data or None,
            "rug_check_data": coin.rug_check_data or None,
        } if coin else None

    async def mark_unposted_as_posted(self):
        """Обновляет все записи с is_posted=False на is_posted=True и возвращает их."""
        stmt = select(BaseCoin).where(BaseCoin.is_posted == False)

        result = await self.session.scalars(stmt)  # Используем scalars()
        coins = result.all()

        for coin in coins:
            coin.is_posted = True

        await self.session.commit()
        return coins  # Возвращаем измененные записи
