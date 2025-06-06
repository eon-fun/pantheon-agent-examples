"""Модульные тесты для Follow Unfollow Bot"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["ray"] = MagicMock()
sys.modules["agents_tools_logger.main"] = MagicMock()

from follow_unfollow_bot.config.config import Config, DBSettings


class TestFollowUnfollowBotConfig:
    """Тесты для конфигурации Follow Unfollow Bot"""

    def test_db_settings_creation(self):
        """Тест создания настроек БД"""
        db_settings = DBSettings(user="test_user")
        assert db_settings.user == "test_user"
        assert db_settings.password == "postgres"

    def test_db_url_property(self):
        """Тест генерации URL для БД"""
        db_settings = DBSettings(user="test_user", password="test_pass")
        expected_url = "postgresql+asyncpg://test_user:test_pass@localhost:5432/postgres"
        assert db_settings.url == expected_url

    def test_config_defaults(self):
        """Тест основной конфигурации"""
        with patch.dict(os.environ, {"DB_USER": "test_user"}):
            config = Config()
            assert config.app_title == "follow_unfollow_bot"
            assert config.max_followers_per_day == 400

    def test_config_check_configuration(self):
        """Тест проверки конфигурации"""
        with patch.dict(os.environ, {"DB_USER": "test_user"}):
            config = Config()
            config.check_configuration()
