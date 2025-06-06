"""Модульные тесты для AI Predicts Manager - Results"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["database.redis.redis_client"] = MagicMock()

from results import AsyncResultsAnalyzer


class TestAsyncResultsAnalyzer:
    """Тесты для класса AsyncResultsAnalyzer"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.analyzer = AsyncResultsAnalyzer()

    def test_init(self):
        """Тест инициализации AsyncResultsAnalyzer"""
        assert self.analyzer.executor is not None
        assert hasattr(self.analyzer, "executor")

    def test_del_method(self):
        """Тест метода __del__"""
        analyzer = AsyncResultsAnalyzer()
        # Проверяем что метод не вызывает исключений
        analyzer.__del__()

    @pytest.mark.asyncio
    async def test_debug_signal_storage_basic(self):
        """Тест базовой функциональности debug_signal_storage"""
        with patch("results.db") as mock_db:
            mock_db.r.zrangebyscore.return_value = []

            result = await self.analyzer.debug_signal_storage("BTC", "LONG")

            # Метод должен выполниться без ошибок
            mock_db.r.zrangebyscore.assert_called_once()
