"""Модульные тесты для AI Predicts Manager - Technical Analysis"""

import os
import sys

import pytest

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from technical import TechnicalAnalysis


class TestTechnicalAnalysis:
    """Тесты для класса TechnicalAnalysis"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.ta = TechnicalAnalysis()

    @pytest.mark.asyncio
    async def test_calculate_vwap_empty_candles(self):
        """Тест VWAP с пустыми свечами"""
        result = await self.ta.calculate_vwap([])
        assert result == []

    @pytest.mark.asyncio
    async def test_calculate_vwap_single_candle(self):
        """Тест VWAP с одной свечей"""
        candles = [{"high": 100, "low": 90, "close": 95, "volume": 1000}]
        result = await self.ta.calculate_vwap(candles)

        # VWAP = (high + low + close) / 3 = (100 + 90 + 95) / 3 = 95
        assert len(result) == 1
        assert abs(result[0] - 95.0) < 0.001

    @pytest.mark.asyncio
    async def test_calculate_vwap_multiple_candles(self):
        """Тест VWAP с несколькими свечами"""
        candles = [
            {"high": 100, "low": 90, "close": 95, "volume": 1000},
            {"high": 110, "low": 100, "close": 105, "volume": 2000},
        ]
        result = await self.ta.calculate_vwap(candles)

        assert len(result) == 2
        assert isinstance(result[0], float)
        assert isinstance(result[1], float)
