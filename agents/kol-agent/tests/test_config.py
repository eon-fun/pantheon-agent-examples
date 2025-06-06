"""Модульные тесты для KOL Agent"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["ray"] = MagicMock()
sys.modules["langfuse.callback"] = MagicMock()

from kol_agent.config import Config, get_config


class TestKolAgentConfig:
    """Тесты для конфигурации KOL Agent"""

    def test_config_defaults(self):
        """Тест настроек по умолчанию"""
        with patch.dict(
            os.environ, {"LANGFUSE_SECRET_KEY": "test", "LANGFUSE_PUBLIC_KEY": "test", "LANGFUSE_HOST": "test"}
        ):
            config = Config()
            assert config.LIKE_PERCENTAGE == 0.9
            assert config.COMMENT_PERCENTAGE == 0.6

    def test_get_config_function(self):
        """Тест функции get_config"""
        with patch.dict(
            os.environ, {"LANGFUSE_SECRET_KEY": "test", "LANGFUSE_PUBLIC_KEY": "test", "LANGFUSE_HOST": "test"}
        ):
            config = get_config()
            assert config.LIKE_PERCENTAGE == 0.9

    def test_config_percentages_valid(self):
        """Тест валидности процентных настроек"""
        with patch.dict(
            os.environ, {"LANGFUSE_SECRET_KEY": "test", "LANGFUSE_PUBLIC_KEY": "test", "LANGFUSE_HOST": "test"}
        ):
            config = Config()
            assert 0.0 <= config.LIKE_PERCENTAGE <= 1.0

    def test_langfuse_keys_required(self):
        """Тест обязательности ключей Langfuse"""
        with patch.dict(
            os.environ,
            {
                "LANGFUSE_SECRET_KEY": "secret123",
                "LANGFUSE_PUBLIC_KEY": "public456",
                "LANGFUSE_HOST": "https://example.com",
            },
        ):
            config = Config()
            assert len(config.LANGFUSE_SECRET_KEY) > 0
