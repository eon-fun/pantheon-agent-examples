import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apy_agent import APYAgent


class TestAPYAgentAsync:
    def setup_method(self):
        self.agent = APYAgent("test-api-key")

    @pytest.mark.asyncio
    async def test_find_best_pool_success(self):
        protocols_data = [{"name": "Uniswap", "slug": "uniswap", "chains": [{"id": 1}]}]
        defi_tokens_data = {
            "data": [
                {
                    "address": "0x123",
                    "chainId": 1,
                    "apy": 5.5,
                    "type": "liquidity-pool",
                    "protocolSlug": "uniswap",
                    "primaryAddress": "0xabc",
                    "decimals": 18,
                    "underlyingTokens": [{"address": "0x456"}, {"address": "0x789"}],
                }
            ]
        }
        with (
            patch.object(self.agent, "get_protocols", return_value=protocols_data),
            patch.object(self.agent, "get_defi_tokens", return_value=defi_tokens_data),
            patch.object(self.agent, "is_valid_pool", return_value=True),
        ):
            result = await self.agent.find_best_pool("0x456", chain_id=1)
            assert result["protocol"] == "uniswap"
            assert result["apy"] == 5.5
            assert len(result["found_pools"]) == 1

    @pytest.mark.asyncio
    async def test_find_best_pool_no_matching_tokens(self):
        protocols_data = [{"name": "Uniswap", "slug": "uniswap", "chains": [{"id": 1}]}]
        defi_tokens_data = {"data": []}
        with (
            patch.object(self.agent, "get_protocols", return_value=protocols_data),
            patch.object(self.agent, "get_defi_tokens", return_value=defi_tokens_data),
        ):
            result = await self.agent.find_best_pool("0x456", chain_id=1)
            assert result["protocol"] is None
            assert result["apy"] == 0
