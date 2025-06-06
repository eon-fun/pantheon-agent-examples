import os
import sys
import time
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apy_agent import APYAgent


class TestAPYAgentExtended:
    def setup_method(self):
        self.agent = APYAgent("test-api-key")

    @patch("apy_agent.requests.get")
    def test_get_defi_tokens_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "address": "0x123",
                    "chainId": 1,
                    "apy": 5.5,
                    "type": "liquidity-pool",
                    "protocolSlug": "uniswap",
                    "underlyingTokens": [{"address": "0x456"}, {"address": "0x789"}],
                }
            ]
        }
        mock_get.return_value = mock_response
        result = self.agent.get_defi_tokens(chain_id=1, protocol_slug="uniswap")
        assert "data" in result
        assert len(result["data"]) == 1

    @patch("apy_agent.requests.get")
    def test_get_defi_tokens_without_protocol(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        result = self.agent.get_defi_tokens(chain_id=1)
        assert "data" in result
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert "protocolSlug" not in params

    def test_is_token_active_outdated_timestamp(self):
        old_timestamp = int(time.time()) - 100000
        price_data = {"price": "1.5", "timestamp": str(old_timestamp)}
        with patch.object(self.agent, "get_token_price", return_value=price_data):
            result = self.agent.is_token_active("0x123")
            assert result is False
