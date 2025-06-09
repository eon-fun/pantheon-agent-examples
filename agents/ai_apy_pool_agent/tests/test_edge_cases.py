import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apy_agent import APYAgent


class TestEdgeCases:
    def setup_method(self):
        self.agent = APYAgent("test-api-key")

    def test_is_valid_pool_insufficient_underlying_tokens(self):
        pool = {
            "apy": 10,
            "underlyingTokens": [{"address": "0x123"}],  # Only 1 token instead of 2
            "chainId": 1,
        }
        result = self.agent.is_valid_pool(pool, apy=10)
        assert result is False

    def test_is_valid_pool_inactive_underlying_token(self):
        pool = {
            "apy": 10,
            "underlyingTokens": [{"address": "0x123"}, {"address": "0x456"}],
            "chainId": 1,
            "address": "0xpool",
            "decimals": 18,
            "type": "lp",
            "protocolSlug": "uniswap",
            "primaryAddress": "0xprimary",
        }
        with patch.object(self.agent, "is_token_active", side_effect=[True, False]):
            result = self.agent.is_valid_pool(pool, apy=10)
            assert result is False

    def test_is_valid_pool_missing_required_fields(self):
        pool = {
            "apy": 10,
            "underlyingTokens": [{"address": "0x123"}, {"address": "0x456"}],
            "chainId": 1,
            # Missing required fields: address, decimals, type, protocolSlug
        }
        with patch.object(self.agent, "is_token_active", return_value=True):
            result = self.agent.is_valid_pool(pool, apy=10)
            assert result is False

    @pytest.mark.asyncio
    async def test_find_best_pool_unsupported_chain(self):
        protocols = [
            {
                "name": "Uniswap V3",
                "slug": "uniswap-v3",
                "chains": [{"id": 137}],  # Only supports chain 137, not 1
            }
        ]

        with patch.object(self.agent, "get_protocols", return_value=protocols):
            result = await self.agent.find_best_pool("0x123", chain_id=1)
            assert result["protocol"] is None
            assert result["apy"] == 0

    @pytest.mark.asyncio
    async def test_find_best_pool_no_matching_tokens(self):
        protocols = [{"name": "Uniswap V3", "slug": "uniswap-v3", "chains": [{"id": 1}]}]

        tokens = [
            {
                "address": "0x999",  # Different from searched token
                "apy": 10,
                "underlyingTokens": [{"address": "0x111"}, {"address": "0x222"}],
            }
        ]

        with patch.object(self.agent, "get_protocols", return_value=protocols):
            with patch.object(self.agent, "get_defi_tokens", return_value=tokens):
                result = await self.agent.find_best_pool("0x123", chain_id=1)
                assert result["protocol"] is None

    @pytest.mark.asyncio
    async def test_find_best_pool_exception_handling(self):
        protocols = [{"name": "Uniswap V3", "slug": "uniswap-v3", "chains": [{"id": 1}]}]

        with patch.object(self.agent, "get_protocols", return_value=protocols):
            with patch.object(self.agent, "get_defi_tokens", side_effect=Exception("API Error")):
                result = await self.agent.find_best_pool("0x123", chain_id=1)
                # Should continue and return empty result instead of crashing
                assert result["protocol"] is None
                assert result["apy"] == 0

    @pytest.mark.asyncio
    async def test_find_best_pool_invalid_pool(self):
        protocols = [{"name": "Uniswap V3", "slug": "uniswap-v3", "chains": [{"id": 1}]}]

        tokens = [
            {
                "address": "0x123",
                "apy": 10,
                "underlyingTokens": [{"address": "0x111"}],  # Only 1 token - invalid
                "chainId": 1,
            }
        ]

        with patch.object(self.agent, "get_protocols", return_value=protocols):
            with patch.object(self.agent, "get_defi_tokens", return_value=tokens):
                with patch.object(self.agent, "is_valid_pool", return_value=False):
                    result = await self.agent.find_best_pool("0x123", chain_id=1)
                    assert result["protocol"] is None
                    assert len(result["found_pools"]) == 0

    def test_format_investment_recommendation_with_underlying_tokens(self):
        best_pool = {
            "protocol": "uniswap",
            "protocol_name": "Uniswap V3",
            "apy": 5.5,
            "type": "liquidity-pool",
            "token_address": "0x123",
            "primary_address": "0xabc",
            "chainId": 1,
            "underlyingTokens": [{"address": "0xtoken1"}, {"address": "0xtoken2"}],
            "found_pools": [
                {
                    "protocol": "uniswap",
                    "protocol_name": "Uniswap V3",
                    "apy": 5.5,
                    "type": "liquidity-pool",
                    "primary_address": "0xabc",
                }
            ],
        }

        price_data = {"price": "1.50", "symbol": "USDC"}
        with patch.object(self.agent, "get_token_price", return_value=price_data):
            result = self.agent.format_investment_recommendation(best_pool)
            assert "USDC: $1.50" in result
            assert "💰 *Токены в пуле:*" in result
