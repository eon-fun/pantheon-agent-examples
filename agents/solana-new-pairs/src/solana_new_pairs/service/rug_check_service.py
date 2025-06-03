from typing import Any

import aiohttp


class RugCheckAPI:
    BASE_URL = "https://api.rugcheck.xyz/v1"

    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def _request(self, endpoint: str) -> dict[str, Any]:
        """Выполняет GET-запрос."""
        async with self.session.get(f"{self.BASE_URL}{endpoint}") as response:
            if response.status != 200:
                raise Exception(f"Error {response.status}: {await response.text()}")
            return await response.json()

    async def get_token_report(self, token_address: str) -> dict[str, Any]:
        """Получает отчёт о токене."""
        endpoint = f"/tokens/{token_address}/report"
        return await self._request(endpoint)

    async def close(self):
        """Закрывает сессию."""
        await self.session.close()


# Пример использования
async def main():
    api = RugCheckAPI()

    try:
        data = await api.get_token_report("5fGA1os23NNWzhGYLhrWAEnwKDgUX2RSUNmgJACcY5hb")  # Пример адреса токена
        print(data)
    finally:
        await api.close()


# import asyncio
#
# asyncio.run(main())
