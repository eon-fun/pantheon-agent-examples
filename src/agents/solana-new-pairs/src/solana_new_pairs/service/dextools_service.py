import logging
import aiohttp
import asyncio
from aiolimiter import AsyncLimiter
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from solana_new_pairs.DB.manager.coin_manager import AlchemyBaseCoinManager
from solana_new_pairs.DB.manager.dex_tools_manager import AlchemyDexToolsManager
from solana_new_pairs.DB.sqlalchemy_database_manager import get_db

logger = logging.getLogger(__name__)


class DextoolsAPIWrapper:
    def __init__(self, api_key: str, plan: str, useragent: str = "API-Wrapper/0.3", requests_per_second: int = 1):
        self._headers = None
        self.url = None
        self._api_key = api_key
        self._useragent = useragent
        self.plan = plan
        self._limiter = AsyncLimiter(requests_per_second, 1)  # Лимит запросов в секунду

        self.set_plan(plan)
        self._session = aiohttp.ClientSession()

    def set_plan(self, plan):
        plan = plan.lower()
        plans = ["free", "trial", "standard", "advanced", "pro"]
        if plan in plans:
            self.plan = plan
            self.url = f"https://public-api.dextools.io/{plan}/v2"
        elif plan == "partner":
            self.plan = plan
            self.url = "https://api.dextools.io/v2"
        else:
            raise ValueError("Plan not found")

        self._headers = {
            "X-API-Key": self._api_key,
            "Accept": "application/json",
            "User-Agent": self._useragent,
        }
        logger.debug(f"Plan URL: {self.url}")
        logger.info(f"Set up plan: {plan}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self._session.close()

    async def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None):
        async with self._limiter:  # Ограничение запросов
            url = f"{self.url}{endpoint}"
            async with self._session.get(url, headers=self._headers, params=params) as response:
                if response.status == 403:
                    response.raise_for_status()
                    raise Exception(f"Access denied (403). Check your API key or request limits.")
                response.raise_for_status()
                return await response.json()

    async def get_blockchain(self, chain: str):
        return await self._request(f"/blockchain/{chain}")

    async def get_blockchains(self, order="asc", sort="name", page=None, pageSize=None):
        return await self._request("/blockchain",
                                   params={"order": order, "sort": sort, "page": page, "pageSize": pageSize})

    async def get_pool_by_address(self, chain: str, address: str):
        return await self._request(f"/pool/{chain}/{address}")

    async def get_pools(self, chain, from_, to, order="asc", sort="creationTime", page=None, pageSize=None):
        """
        {'creationTime': '2023-11-14T19:08:19.601Z',
        'exchange': {'
                    name': 'Raydium',
                    'factory': '675kpx9mhtjs2zt1qfr1nyhuzelxfqm9h24wfsut1mp8'
                    },
        'address': '8f94e3kYk9ZPuEPT5Zgo9tiVJvwaj8zUzbPFPqt2MKK2',
        'mainToken': {
                'name': 'TABOO TOKEN',
                'symbol': 'TABOO',
                'address': 'kWnW2tpHHabrwPFbE1ZhdVQqdqyEfGE1JW9pVeVo3UL'
        },
        'sideToken': {
                'name': 'Wrapped SOL',
                'symbol': 'SOL',
                'address': 'So11111111111111111111111111111111111111112'}
        }
        """
        params = {
            "from": from_,
            "to": to,
            "order": order,
            "sort": sort,
            "page": page,
            "pageSize": pageSize,
        }

        # Убираем параметры со значением None
        params = {k: v for k, v in params.items() if v is not None}

        return await self._request(f"/pool/{chain}", params=params)




async def main():
    API_KEY = "Kv7BZ8mwvU4vFoaaS8eEJ3UvmXG4x7Qk71uLesRF"  # Укажите ваш API-ключ
    api = DextoolsAPIWrapper(api_key=API_KEY, plan='trial')  # Лимит: 2 запроса в секунду

    try:
        # print(await api.get_blockchains(order="asc", sort="name", page=1, pageSize=50))
        data = await api.get_pools(chain="solana", from_="2023-11-14T19:00:00", to="2023-11-14T23:00:00", order="asc",
                                   sort="creationTime", page=None, pageSize=None)
        print(data)
    finally:
        await api.close()


# https://public-api.dextools.io/trial/v2/pool/ether
# https://public-api.dextools.io/trial/v2/pool/ether
# asyncio.run(main())

async def collect_and_store_data(dex_tools_api: DextoolsAPIWrapper):
    now = datetime.now(timezone.utc)
    from_ = (now - timedelta(seconds=60)).isoformat(timespec='seconds')  # Дата 10 секунд назад
    to = now.isoformat(timespec='seconds')  # Текущая дата
    chain = "solana"
    data = await dex_tools_api.get_pools(chain, from_=from_, to=to)
    if data:
        print(f"Received {len(data.get('data', []))} pools in timeframe {from_} - {to}")
        data = data.get('data').get('results')
        async for session in get_db():
            coin_manager = AlchemyBaseCoinManager(session)
            dex_tools_manager = AlchemyDexToolsManager(session)
            for pool_data in data:
                token_address = pool_data.get('mainToken').get('address')
                try:
                    new_coin = await coin_manager.create_base_coin(token_address)
                    await dex_tools_manager.create_dex_tools_data(new_coin.id, pool_data)
                except Exception as e:
                    print(f"We already have dextools data for {new_coin.id}")

    else:
        print("No data received")
