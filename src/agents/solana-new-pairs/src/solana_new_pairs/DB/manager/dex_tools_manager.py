from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from solana_new_pairs.DB.manager.base import BaseAlchemyManager
from solana_new_pairs.DB.models.coin_model import BaseCoin
from solana_new_pairs.DB.models.dex_tools_model import DexToolsData
from solana_new_pairs.utils.utils import clean_json


class AlchemyDexToolsManager(BaseAlchemyManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_dex_tools_data(self, base_coin_id: int, data: dict):
        """Создает новую запись в таблице DexToolsData"""
        data = clean_json(data)
        self.session.add(DexToolsData(base_coin_id=base_coin_id, data=data))