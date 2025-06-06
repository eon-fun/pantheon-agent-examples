"""Модульные тесты для Twitter Echo Bot Config"""

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["base_agent"] = MagicMock()
sys.modules["base_agent.ray_entrypoint"] = MagicMock()
sys.modules["tweetscout_utils"] = MagicMock()
sys.modules["tweetscout_utils.main"] = MagicMock()
sys.modules["send_openai_request"] = MagicMock()
sys.modules["send_openai_request.main"] = MagicMock()


class TestEchoBotConfig:
    def test_fastapi_settings(self):
        """Тест настроек FastAPI"""
        from twitter_echo_bot.config.config import FastAPISettings

        settings = FastAPISettings()
        assert "http://localhost:8080" in settings.allowed_origins
        assert "GET" in settings.allowed_methods
        assert "POST" in settings.allowed_methods
        assert "Content-Type" in settings.allowed_headers
        assert settings.allowed_credentials is True

    def test_database_settings(self):
        """Тест настроек базы данных"""
        from twitter_echo_bot.config.config import DatabaseSettings

        settings = DatabaseSettings()
        assert settings.db_user == "rag"
        assert settings.db_password == "rag"
        assert settings.db_host == "localhost"
        assert settings.db_port == "5432"
        assert settings.db_name == "rag"

    def test_database_url_generation(self):
        """Тест генерации URL базы данных"""
        from twitter_echo_bot.config.config import DatabaseSettings

        settings = DatabaseSettings()
        expected_url = "postgresql+asyncpg://rag:rag@localhost:5432/rag"
        assert settings.url == expected_url

    def test_app_config(self):
        """Тест общей конфигурации приложения"""
        from twitter_echo_bot.config.config import AppConfig

        config = AppConfig()
        assert config.app_title == "Twitter Echo Bot"
        assert config.app_description == "API for Twitter Echo Bot"
        assert config.app_version == "0.0.1"
