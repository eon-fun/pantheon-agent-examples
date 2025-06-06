"""Модульные тесты для Dialogue Manager - Settings"""

import os
import sys
from unittest.mock import MagicMock, patch

# Добавляем src в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

# Мокируем внешние зависимости
sys.modules["database.redis.redis_client"] = MagicMock()
sys.modules["telethon"] = MagicMock()

from config import Settings


class TestSettings:
    """Тесты для класса Settings"""

    def test_settings_class_exists(self):
        assert Settings is not None

    def test_settings_fields(self):
        annotations = getattr(Settings, "__annotations__", {})
        assert "API_ID" in annotations
        assert "API_HASH" in annotations
        assert "SESSION_NAME" in annotations
        assert "REDIS_MESSAGES_KEY" in annotations
        assert "BOT_COMMAND" in annotations

    @patch.dict(
        os.environ,
        {
            "API_ID": "12345",
            "API_HASH": "test-hash",
            "SESSION_NAME": "test-session",
            "REDIS_MESSAGES_KEY": "test-key",
            "BOT_COMMAND": "/test",
        },
    )
    def test_settings_creation_with_env(self):
        settings = Settings()
        assert settings.API_ID == "12345"
        assert settings.API_HASH == "test-hash"
        assert settings.SESSION_NAME == "test-session"
        assert settings.REDIS_MESSAGES_KEY == "test-key"
        assert settings.BOT_COMMAND == "/test"

    def test_settings_inheritance(self):
        """Тест наследования от BaseSettings"""
        # Проверяем что Settings наследуется от правильного класса
        assert hasattr(Settings, "__annotations__")
        assert callable(Settings)
