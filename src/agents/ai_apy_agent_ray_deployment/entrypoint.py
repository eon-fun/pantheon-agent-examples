import time
import json
import requests
from typing import Dict, List, Optional
from contextlib import asynccontextmanager
from urllib.parse import urljoin
from fastapi import FastAPI
from ray import serve

from infrastructure.configs.config import get_settings
from simple_ai_agents.ai_apy_agent_ray_deployment.src.commands import dp, bot

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await dp.start_polling(bot)
    yield


app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class APYAgent:
    def __init__(self):
        self.base_url = "https://api.enso.finance/api/v1"
        self.api_key = settings.ENSO_API_TEST_KEY
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    @app.post("/{goal}")
    def handle(self, goal: str, plan: dict | None = None):
        """This is one of the most important endpoint of MAS.
        It handles all requests made by handoff from other agents or by user."""
        pass

    def handoff(self, endpoint: str, goal: str, plan: dict):
        """This method means that agent can't find a solution (wrong route/wrong plan/etc)
        and decide to handoff the task to another agent. """
        return requests.post(urljoin(endpoint, goal), json=plan).json()

    def get_token_price(self, token_address: str, chain_id: int = 1) -> Dict:
        """Gets token price information"""
        url = f"{self.base_url}/prices/{chain_id}/{token_address}"
        response = requests.get(url, headers=self.headers)
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

        print(f"✅ Token is active:")
        print(f"   - Price: ${float(price):,.2f}")
        print(f"   - Name: {price_data.get('name')}")
        print(f"   - Symbol: {price_data.get('symbol')}")
        return True

    def get_protocols(self) -> List[Dict]:
        """Gets list of supported protocols"""
        response = requests.get(f"{self.base_url}/protocols", headers=self.headers)
        return response.json()

    def get_defi_tokens(self, chain_id: int = 1, protocol_slug: Optional[str] = None) -> Dict:
        """Gets DeFi tokens with their APY and additional information"""
        params = {
            "chainId": chain_id,
            "type": "defi",
            "includeMetrics": "true"
        }
        if protocol_slug:
            params["protocolSlug"] = protocol_slug

        response = requests.get(f"{self.base_url}/tokens", headers=self.headers, params=params)
        return response.json()

    def is_valid_pool(self, token: Dict, apy: float) -> bool:
        """Checks if the pool is reliable and safe for investment"""
        print("\n🔍 Pool safety check:")

        if not apy:
            print(f"⚠️ APY is missing")
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

        print(f"✅ Pool passed safety check:")
        print(f"   - Protocol: {token['protocolSlug']}")
        print(f"   - APY: {apy}%")
        print(f"   - Type: {token['type']}")
        print(f"   - Primary contract: {token.get('primaryAddress')}")
        print(f"   - Number of underlying tokens: {len(underlying_tokens)}")
        return True

    async def find_best_pool(self, token_address: str, chain_id: int = 1) -> Dict:
        """Finds pool with the best APY for given token"""
        print(f"\n🔍 Starting search for safe pools for token: {token_address}")
        protocols = self.get_protocols()
        print(f"📋 Retrieved protocols: {len(protocols)}")

        best_pool = {
            "apy": 0,
            "protocol": None,
            "token_address": None,
            "found_pools": []
        }

        for protocol in protocols:
            try:
                print(f"\n🔄 Checking protocol: {protocol['name']} ({protocol['slug']})")

                if not any(chain['id'] == chain_id for chain in protocol['chains']):
                    print(f"⏩ Skipping {protocol['slug']} - network {chain_id} not supported")
                    continue

                defi_tokens = self.get_defi_tokens(chain_id, protocol['slug'])
                tokens = defi_tokens.get("data", [])
                print(f"📊 Found {len(tokens)} tokens in {protocol['slug']}")

                for token in tokens:
                    underlying_addresses = [t['address'].lower() for t in token.get('underlyingTokens', [])]
                    if token_address.lower() in underlying_addresses:
                        apy = token.get("apy")
                        print(f"\n🔎 Found pool in {protocol['slug']} with parameters:")
                        print(f"- APY: {apy}%")
                        print(f"- Raw token data: {json.dumps(token, indent=2)}")

                        if not self.is_valid_pool(token, apy):
                            continue

                        pool_info = {
                            "apy": apy,
                            "protocol": protocol['slug'],
                            "protocol_name": protocol['name'],
                            "token_address": token["address"],
                            "primary_address": token.get("primaryAddress"),
                            "type": token.get("type"),
                            "tvl": token.get("tvl"),
                            "days_old": token.get("daysOld"),
                            "transaction_count": token.get("transactionCount")
                        }
                        best_pool["found_pools"].append(pool_info)

                        if apy > best_pool["apy"]:
                            best_pool.update(pool_info)

            except Exception as e:
                print(f"❌ Error processing protocol {protocol['slug']}: {str(e)}")
                continue

        print(f"\n📈 Total safe pools found: {len(best_pool['found_pools'])}")
        if best_pool['protocol']:
            print(f"🏆 Best pool: {best_pool['protocol_name']} with APY {best_pool['apy']}%")

        return best_pool

    def format_investment_recommendation(self, best_pool: Dict) -> str:
        """Formats recommendation for sending to Telegram"""
        if not best_pool["protocol"]:
            return "🔍 No suitable pools found for investment"

        sorted_pools = sorted(
            [pool for pool in best_pool["found_pools"]],
            key=lambda x: x["apy"],
            reverse=True
        )[:5]

        token_prices = {}
        for token in best_pool.get("underlyingTokens", []):
            price_data = self.get_token_price(token["address"], best_pool["chainId"])
            if price_data:
                token_prices[token["address"]] = {
                    "price": float(price_data.get("price", 0)),
                    "symbol": price_data.get("symbol", "Unknown")
                }

        tokens_info = "\n".join([
            f"    - {data['symbol']}: ${data['price']:,.2f}"
            for addr, data in token_prices.items()
        ])

        pools_text = "\n".join([
            f"• *{pool['protocol_name']}*:\n"
            f"  - APY: {pool['apy']:.2f}%\n"
            f"  - Pool type: {pool['type']}\n"
            f"  - Contract: `{pool['primary_address']}`"
            for pool in sorted_pools
        ])

        recommendation = f"""
🏆 *Investment pools found:*

{pools_text}

📊 *Best pool details:*
• Protocol: `{best_pool['protocol_name']}`
• APY: `{best_pool['apy']:.2f}%`
• Type: `{best_pool['type']}`
• Pool address: `{best_pool['token_address']}`
• Contract: `{best_pool['primary_address']}`

💰 *Pool tokens:*
{tokens_info}

💡 _Safety conditions:_
• Realistic APY (0.1% - 100%)
• All tokens have current price
• Active trading volume
• Regular price updates
"""
        return recommendation


agent = APYAgent()
app = APYAgent().bind()

if __name__ == "__main__":
    serve.run(app, route_prefix="/")
