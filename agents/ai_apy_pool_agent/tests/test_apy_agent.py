"""Модульные тесты для APY Agent"""

import os
import sys
import time
from unittest.mock import MagicMock, patch

# Добавляем родительскую директорию в sys.path для импорта apy_agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apy_agent import APYAgent


class TestAPYAgent:
    """Тесты для класса APYAgent"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.agent = APYAgent("test-api-key")

    @patch("apy_agent.requests.get")
    def test_get_token_price_success(self, mock_get):
        """Тест успешного получения цены токена"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "price": "1.50",
            "name": "Test Token",
            "symbol": "TEST",
            "timestamp": str(int(time.time())),
        }
        mock_get.return_value = mock_response

        result = self.agent.get_token_price("0x123", 1)

        assert result["price"] == "1.50"
        assert result["name"] == "Test Token"
        assert result["symbol"] == "TEST"
        mock_get.assert_called_once()

    @patch("apy_agent.requests.get")
    def test_get_token_price_failure(self, mock_get):
        """Тест неудачного получения цены токена"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = self.agent.get_token_price("0x123", 1)

        assert result is None

    @patch("apy_agent.requests.get")
    def test_get_protocols_success(self, mock_get):
        """Тест успешного получения протоколов"""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "Uniswap", "slug": "uniswap", "chains": [{"id": 1}]},
            {"name": "Aave", "slug": "aave", "chains": [{"id": 1}]},
        ]
        mock_get.return_value = mock_response

        result = self.agent.get_protocols()

        assert len(result) == 2
        assert result[0]["name"] == "Uniswap"
        mock_get.assert_called_once()

    def test_is_token_active_no_price_data(self):
        """Тест проверки активности токена без данных о цене"""
        with patch.object(self.agent, "get_token_price", return_value=None):
            result = self.agent.is_token_active("0x123")
            assert result is False

    def test_is_token_active_zero_price(self):
        """Тест проверки активности токена с нулевой ценой"""
        price_data = {"price": "0", "timestamp": str(int(time.time()))}
        with patch.object(self.agent, "get_token_price", return_value=price_data):
            result = self.agent.is_token_active("0x123")
            assert result is False

    def test_is_token_active_valid_token(self):
        """Тест проверки активности валидного токена"""
        price_data = {"price": "1.5", "timestamp": str(int(time.time())), "name": "Test Token", "symbol": "TEST"}
        with patch.object(self.agent, "get_token_price", return_value=price_data):
            result = self.agent.is_token_active("0x123")
            assert result is True

    def test_is_valid_pool_no_apy(self):
        """Тест проверки пула без APY"""
        token = {"chainId": 1, "address": "0x123"}
        result = self.agent.is_valid_pool(token, None)
        assert result is False

    def test_is_valid_pool_high_apy(self):
        """Тест проверки пула с подозрительно высоким APY"""
        token = {"chainId": 1, "address": "0x123"}
        result = self.agent.is_valid_pool(token, 150.0)
        assert result is False

    def test_is_valid_pool_low_apy(self):
        """Тест проверки пула со слишком низким APY"""
        token = {"chainId": 1, "address": "0x123"}
        result = self.agent.is_valid_pool(token, 0.05)
        assert result is False

    def test_is_valid_pool_valid(self):
        """Тест проверки валидного пула"""
        token = {
            "chainId": 1,
            "address": "0x123",
            "decimals": 18,
            "type": "liquidity-pool",
            "protocolSlug": "uniswap",
            "primaryAddress": "0xabc",
            "underlyingTokens": [{"address": "0x456"}, {"address": "0x789"}],
        }
        with patch.object(self.agent, "is_token_active", return_value=True):
            result = self.agent.is_valid_pool(token, 5.0)
            assert result is True

    def test_format_investment_recommendation_no_pools(self):
        """Тест форматирования рекомендации без пулов"""
        best_pool = {"protocol": None, "found_pools": []}
        result = self.agent.format_investment_recommendation(best_pool)
        assert "Не найдено подходящих пулов" in result
