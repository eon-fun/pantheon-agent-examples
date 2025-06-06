import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apy_agent import APYAgent


class TestTelegramHandlers:
    def setup_method(self):
        self.agent = APYAgent("test-api-key")

    def test_format_investment_recommendation_with_pools(self):
        best_pool = {
            "protocol": "uniswap",
            "protocol_name": "Uniswap V3",
            "apy": 5.5,
            "type": "liquidity-pool",
            "token_address": "0x123",
            "primary_address": "0xabc",
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
            assert "Найденные пулы для инвестирования" in result
            assert "Uniswap V3" in result
            assert "5.50%" in result

    def test_format_investment_recommendation_no_token_prices(self):
        best_pool = {
            "protocol": "uniswap",
            "protocol_name": "Uniswap V3",
            "apy": 5.5,
            "type": "liquidity-pool",
            "token_address": "0x123",
            "primary_address": "0xabc",
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
        with patch.object(self.agent, "get_token_price", return_value=None):
            result = self.agent.format_investment_recommendation(best_pool)
            assert "Найденные пулы для инвестирования" in result
