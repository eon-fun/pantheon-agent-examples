"""Модульные тесты для AI Predicts Manager - Collector"""

import os
import sys
from unittest.mock import MagicMock

import pytest

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["aiohttp"] = MagicMock()
sys.modules["ccxt.async_support"] = MagicMock()

from collector import AsyncRateLimiter


class TestAsyncRateLimiter:
    """Тесты для класса AsyncRateLimiter"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.rate_limiter = AsyncRateLimiter()

    def test_init(self):
        """Тест инициализации AsyncRateLimiter"""
        assert "binance" in self.rate_limiter.limits
        assert "coingecko" in self.rate_limiter.limits
        assert "binance" in self.rate_limiter.locks
        assert "coingecko" in self.rate_limiter.locks

    def test_limits_configuration(self):
        """Тест конфигурации лимитов"""
        binance_limit = self.rate_limiter.limits["binance"]
        coingecko_limit = self.rate_limiter.limits["coingecko"]

        assert binance_limit["limit"] == 1200
        assert binance_limit["window"] == 60
        assert coingecko_limit["limit"] == 50
        assert coingecko_limit["window"] == 60

    @pytest.mark.asyncio
    async def test_check_and_wait_within_limit(self):
        """Тест проверки лимитов в пределах нормы"""
        self.rate_limiter.limits["binance"]["calls"] = 100
        await self.rate_limiter.check_and_wait("binance")
        assert self.rate_limiter.limits["binance"]["calls"] == 101
