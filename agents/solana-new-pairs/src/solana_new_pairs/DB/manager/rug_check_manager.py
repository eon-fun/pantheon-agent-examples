from solana_new_pairs.DB.manager.base import BaseAlchemyManager
from solana_new_pairs.DB.models.rug_check_model import RugCheckData
from sqlalchemy.ext.asyncio import AsyncSession


class AlchemyRugCheckDataManager(BaseAlchemyManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_rug_check_data(self, base_coin_id: int, data: dict):
        """Создает новую запись в таблице RugCheckData"""
        self.session.add(RugCheckData(base_coin_id=base_coin_id, data=data))
