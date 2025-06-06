import asyncio
import json
import time
from contextlib import asynccontextmanager

import requests
from apy_agent.commands import bot, dp
from apy_agent.config import get_settings
from apy_agent.templates.messages import render_recommendation_message
from base_agent.ray_entrypoint import BaseAgent
from fastapi import FastAPI
from ray import serve

HEADERS = {"accept": "application/json", "Authorization": f"Bearer {get_settings().ENSO_API_KEY}"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(bot_polling())
    yield


app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class APYAgent(BaseAgent):
    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None):
        print(f"\n🤖 Получена команда поиска пулов от пользователя {goal.from_user.username}")
        try:
            token_address = goal.text.split()[1]
            print(f"📝 Получен адрес токена: {token_address}")
        except IndexError:
            print("⚠️ Пользователь не указал адрес токена")
            await goal.answer(
                "⚠️ Пожалуйста, укажите адрес токена.\nПример: `/find_pools 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`",
                parse_mode="Markdown",
            )
            return
        status_message = await goal.answer("🔍 Ищу лучшие пулы для инвестирования...")

        try:
            best_pool = await self.find_best_pool(token_address)

            recommendation = self.format_investment_recommendation(best_pool)
            await status_message.edit_text(recommendation, parse_mode="Markdown")

        except Exception as e:
            error_message = f"❌ Произошла ошибка при поиске пулов: {str(e)}"
            await status_message.edit_text(error_message)

    def get_token_price(self, token_address: str, chain_id: int = 1) -> dict:
        """Gets token price information"""
        url = f"{get_settings().BASE_URL}/prices/{chain_id}/{token_address}"
        response = requests.get(url, headers=HEADERS)
        return response.json() if response.status_code == 200 else None

    def is_token_active(self, token_address: str, chain_id: int = 1) -> bool:
        """Checks token activity based on price data"""
        price_data = self.get_token_price(token_address, chain_id)
        if not price_data:
            print("⚠️ Failed to get price data")
            return False

        price = price_data.get("price")
        if not price or float(price) == 0:
            print("⚠️ Token has no current price")
            return False

        timestamp = price_data.get("timestamp")
        if timestamp:
            current_time = int(time.time())
            if current_time - int(timestamp) > 86400:
                print("⚠️ Price data is outdated")
                return False

        print("✅ Token is active:")
        print(f"   - Price: ${float(price):,.2f}")
        print(f"   - Name: {price_data.get('name')}")
        print(f"   - Symbol: {price_data.get('symbol')}")
        return True

    def get_protocols(self) -> list[dict]:
        """Gets list of supported protocols"""
        response = requests.get(f"{get_settings().BASE_URL}/protocols", headers=HEADERS)
        return response.json()

    def get_defi_tokens(self, chain_id: int = 1, protocol_slug: str | None = None) -> dict:
        """Gets DeFi tokens with their APY and additional information"""
        params = {"chainId": chain_id, "type": "defi", "includeMetrics": "true"}
        if protocol_slug:
            params["protocolSlug"] = protocol_slug

        response = requests.get(f"{get_settings().BASE_URL}/tokens", headers=HEADERS, params=params)
        return response.json()

    def is_valid_pool(self, token: dict, apy: float) -> bool:
        """Checks if the pool is reliable and safe for investment"""
        print("\n🔍 Pool safety check:")

        if not apy:
            print("⚠️ APY is missing")
            return False

        if apy > 100:
            print(f"⚠️ Suspiciously high APY: {apy}%")
            return False

        if apy < 0.1:
            print(f"⚠️ APY too low: {apy}%")
            return False

        underlying_tokens = token.get("underlyingTokens", [])
        if len(underlying_tokens) < 2:
            print("⚠️ Insufficient underlying tokens for pool")
            return False

        for underlying_token in underlying_tokens:
            token_address = underlying_token["address"]
            if not self.is_token_active(token_address, token["chainId"]):
                print(f"⚠️ Underlying token {token_address} is inactive")
                return False

        required_fields = ["chainId", "address", "decimals", "type", "protocolSlug"]
        missing_fields = [field for field in required_fields if field not in token]
        if missing_fields:
            print(f"⚠️ Missing required fields: {', '.join(missing_fields)}")
            return False

        print("✅ Pool passed safety check:")
        print(f"   - Protocol: {token['protocolSlug']}")
        print(f"   - APY: {apy}%")
        print(f"   - Type: {token['type']}")
        print(f"   - Primary contract: {token.get('primaryAddress')}")
        print(f"   - Number of underlying tokens: {len(underlying_tokens)}")
        return True

    async def find_best_pool(self, token_address: str, chain_id: int = 1) -> dict:
        """Finds pool with the best APY for given token"""
        print(f"\n🔍 Starting search for safe pools for token: {token_address}")
        protocols = self.get_protocols()
        print(f"📋 Retrieved protocols: {len(protocols)}")

        best_pool = {"apy": 0, "protocol": None, "token_address": None, "found_pools": []}

        for protocol in protocols:
            try:
                print(f"\n🔄 Checking protocol: {protocol['name']} ({protocol['slug']})")

                if not any(chain["id"] == chain_id for chain in protocol["chains"]):
                    print(f"⏩ Skipping {protocol['slug']} - network {chain_id} not supported")
                    continue

                defi_tokens = self.get_defi_tokens(chain_id, protocol["slug"])
                tokens = defi_tokens.get("data", [])
                print(f"📊 Found {len(tokens)} tokens in {protocol['slug']}")

                for token in tokens:
                    underlying_addresses = [t["address"].lower() for t in token.get("underlyingTokens", [])]
                    if token_address.lower() in underlying_addresses:
                        apy = token.get("apy")
                        print(f"\n🔎 Found pool in {protocol['slug']} with parameters:")
                        print(f"- APY: {apy}%")
                        print(f"- Raw token data: {json.dumps(token, indent=2)}")

                        if not self.is_valid_pool(token, apy):
                            continue

                        pool_info = {
                            "apy": apy,
                            "protocol": protocol["slug"],
                            "protocol_name": protocol["name"],
                            "token_address": token["address"],
                            "primary_address": token.get("primaryAddress"),
                            "type": token.get("type"),
                            "tvl": token.get("tvl"),
                            "days_old": token.get("daysOld"),
                            "transaction_count": token.get("transactionCount"),
                        }
                        best_pool["found_pools"].append(pool_info)

                        if apy > best_pool["apy"]:
                            best_pool.update(pool_info)

            except Exception as e:
                print(f"❌ Error processing protocol {protocol['slug']}: {str(e)}")
                continue

        print(f"\n📈 Total safe pools found: {len(best_pool['found_pools'])}")
        if best_pool["protocol"]:
            print(f"🏆 Best pool: {best_pool['protocol_name']} with APY {best_pool['apy']}%")

        return best_pool

    def format_investment_recommendation(self, best_pool: dict) -> str:
        """Formats recommendation for sending to Telegram"""
        if not best_pool["protocol"]:
            return "🔍 No suitable pools found for investment"

        sorted_pools = sorted([pool for pool in best_pool["found_pools"]], key=lambda x: x["apy"], reverse=True)[:5]

        token_prices = {}
        for token in best_pool.get("underlyingTokens", []):
            price_data = self.get_token_price(token["address"], best_pool["chainId"])
            if price_data:
                token_prices[token["address"]] = {
                    "price": float(price_data.get("price", 0)),
                    "symbol": price_data.get("symbol", "Unknown"),
                }

        tokens_info = "\n".join(
            [f"    - {data['symbol']}: ${data['price']:,.2f}" for addr, data in token_prices.items()]
        )

        pools_text = "\n".join(
            [
                f"• *{pool['protocol_name']}*:\n"
                f"  - APY: {pool['apy']:.2f}%\n"
                f"  - Pool type: {pool['type']}\n"
                f"  - Contract: `{pool['primary_address']}`"
                for pool in sorted_pools
            ]
        )
        result_data = {
            "pools_text": pools_text,
            "best_pool": {
                "protocol_name": best_pool["protocol_name"],
                "apy": best_pool["apy"],
                "type": best_pool["type"],
                "token_address": best_pool["token_address"],
                "primary_address": best_pool["primary_address"],
            },
            "tokens_info": tokens_info,
        }

        recommendation = render_recommendation_message(
            template_path="../../templates/recommendation_message.md.j2", data=result_data
        )
        return recommendation


async def bot_polling():
    await dp.start_polling(bot)


app = APYAgent.bind()

if __name__ == "__main__":
    serve.run(app, route_prefix="/")
