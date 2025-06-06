"""Модульные тесты для APY Agent - Config"""

import os
import sys
from unittest.mock import patch

# Добавляем src в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from config import Settings, get_settings


class TestSettings:
    """Тесты для класса Settings"""

    def test_settings_class_exists(self):
        """Тест существования класса Settings"""
        assert Settings is not None

    def test_settings_fields(self):
        """Тест наличия обязательных полей"""
        annotations = getattr(Settings, "__annotations__", {})
        assert "ENSO_BASE_URL" in annotations
        assert "ENSO_API_KEY" in annotations
        assert "TELEGRAM_BOT_TOKEN_2" in annotations

    @patch.dict(
        os.environ,
        {
            "ENSO_BASE_URL": "https://test.enso.finance",
            "ENSO_API_KEY": "test-api-key",
            "TELEGRAM_BOT_TOKEN_2": "test-bot-token",
        },
    )
    def test_settings_creation_with_env(self):
        """Тест создания Settings с переменными окружения"""
        settings = Settings()
        assert settings.ENSO_BASE_URL == "https://test.enso.finance"
        assert settings.ENSO_API_KEY == "test-api-key"
        assert settings.TELEGRAM_BOT_TOKEN_2 == "test-bot-token"

    def test_get_settings_function(self):
        """Тест функции get_settings"""
        with patch.dict(
            os.environ,
            {
                "ENSO_BASE_URL": "https://test.enso.finance",
                "ENSO_API_KEY": "test-api-key",
                "TELEGRAM_BOT_TOKEN_2": "test-bot-token",
            },
        ):
            get_settings.cache_clear()
            settings = get_settings()
            assert settings.ENSO_BASE_URL == "https://test.enso.finance"
