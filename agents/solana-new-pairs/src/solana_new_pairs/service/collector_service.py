from solana_new_pairs.DB.manager.coin_manager import AlchemyBaseCoinManager
from solana_new_pairs.DB.manager.rug_check_manager import AlchemyRugCheckDataManager
from solana_new_pairs.DB.sqlalchemy_database_manager import get_db
from solana_new_pairs.service.dextools_service import DextoolsAPIWrapper
from solana_new_pairs.service.rug_check_service import RugCheckAPI
from sqlalchemy.ext.asyncio import AsyncSession


async def collect_full_data_about_coin(coin_address: str):
    async for session in get_db():
        coin_manager = AlchemyBaseCoinManager(session)
        coin_data = await coin_manager.get_base_coin_with_all_data(coin_address)
        if coin_data is None:
            coin_data = (await coin_manager.create_base_coin(coin_address)).dict()

        base_coin_id = int(coin_data["id"])
        token_address = coin_data["token_address"]
        creation_time = coin_data["creation_time"]
        if coin_data is None:
            collector_data = await FullDataCollector(
                coin_address, session, base_coin_id=base_coin_id
            ).collect_full_data()
            dex_tools_data = collector_data.get("dex_tools_data")
            token_address = dex_tools_data.get("address")
            creation_time = dex_tools_data.get("creation_time")

            rug_check_data = collector_data.get("rug_check_data")
        else:
            dex_tools_data = coin_data.get("dex_tools_data")
            rug_check_data = coin_data.get("rug_check_data")

            if rug_check_data is None:
                rug_check_data = await FullDataCollector(
                    coin_address, session, base_coin_id
                ).collect_data_from_rug_check()
                rug_check_manager = AlchemyRugCheckDataManager(session)
                await rug_check_manager.create_rug_check_data(coin_data["id"], rug_check_data)
        return {
            "token_address": token_address,
            "creation_time": creation_time,
            "dex_tools_data": dex_tools_data,
            "rug_check_data": rug_check_data,
        }


class FullDataCollector:
    def __init__(self, address, session: AsyncSession, base_coin_id: int):
        self.address = address
        self.session = session
        self.base_coin_id = base_coin_id
        self.chain = "solana"

    async def collect_full_data(self):
        dex_tools_data = await self.collect_data_from_dex_tools()
        rug_check_data = await self.collect_data_from_rug_check()
        return {"dex_tools_data": dex_tools_data, "rug_check_data": rug_check_data}

    async def collect_data_from_rug_check(self):
        rug_check_api = RugCheckAPI()
        try:
            data = await rug_check_api.get_token_report(self.address)
            rug_check_manager = AlchemyRugCheckDataManager(self.session)
            await rug_check_manager.create_rug_check_data(self.base_coin_id, data)
        finally:
            await rug_check_api.close()
        return data

    async def collect_data_from_dex_tools(self):
        dex_tools_api = DextoolsAPIWrapper(api_key="Kv7BZ8mwvU4vFoaaS8eEJ3UvmXG4x7Qk71uLesRF", plan="trial")
        try:
            data = await dex_tools_api.get_pool_by_address(chain=self.chain, address=self.address)

        finally:
            await dex_tools_api.close()
        return data
