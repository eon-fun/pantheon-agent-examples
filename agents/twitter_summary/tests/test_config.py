"""Модульные тесты для Twitter Summary Config"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["aiogram"] = MagicMock()
sys.modules["database"] = MagicMock()
sys.modules["database.redis"] = MagicMock()
sys.modules["database.redis.redis_client"] = MagicMock()


class TestTwitterSummaryConfig:
    @patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_CHANNEL_ID": "test_channel",
            "TWITTER_BEARER_TOKEN": "test_bearer",
            "REDIS_LAST_PROCESSED_TWEETS": "test_tweets",
            "REDIS_SUBSCRIBED_TWITTER_ACCOUNTS": "test_accounts",
        },
    )
    def test_settings_creation(self):
        """Тест создания настроек"""
        from config import Settings

        settings = Settings()
        assert settings.TELEGRAM_BOT_TOKEN == "test_token"
        assert settings.TELEGRAM_CHANNEL_ID == "test_channel"
        assert settings.TWITTER_BEARER_TOKEN == "test_bearer"
        assert settings.REDIS_LAST_PROCESSED_TWEETS == "test_tweets"
        assert settings.REDIS_SUBSCRIBED_TWITTER_ACCOUNTS == "test_accounts"

    @patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "cached_token",
            "TELEGRAM_CHANNEL_ID": "cached_channel",
            "TWITTER_BEARER_TOKEN": "cached_bearer",
            "REDIS_LAST_PROCESSED_TWEETS": "cached_tweets",
            "REDIS_SUBSCRIBED_TWITTER_ACCOUNTS": "cached_accounts",
        },
    )
    def test_get_settings_caching(self):
        """Тест кэширования настроек"""
        from config import get_settings

        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
