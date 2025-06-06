"""Модульные тесты для AI Twitter Summary"""

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["ray"] = MagicMock()
sys.modules["aiohttp"] = MagicMock()
sys.modules["database.redis.redis_client"] = MagicMock()
sys.modules["services.ai_connectors.openai_client"] = MagicMock()

from ray_twitter_summary import TWITTER_BEARER_TOKEN, TWITTER_PROMPT


class TestTwitterSummaryConstants:
    """Тесты для констант и конфигурации"""

    def test_twitter_prompt_exists(self):
        """Тест наличия промпт-шаблона"""
        assert TWITTER_PROMPT is not None
        assert len(TWITTER_PROMPT) > 100
        assert "social media analyst" in TWITTER_PROMPT

    def test_twitter_prompt_content(self):
        """Тест содержания промпт-шаблона"""
        assert "cryptocurrency and celebrity news" in TWITTER_PROMPT
        assert "summarizing tweets" in TWITTER_PROMPT
        assert "HTML formatting" in TWITTER_PROMPT

    def test_twitter_prompt_instructions(self):
        """Тест наличия ключевых инструкций"""
        assert "Combine related tweets" in TWITTER_PROMPT
        assert "main events or announcements" in TWITTER_PROMPT
        assert "possible implications" in TWITTER_PROMPT

    def test_bearer_token_exists(self):
        """Тест наличия Bearer токена"""
        assert TWITTER_BEARER_TOKEN is not None
        assert len(TWITTER_BEARER_TOKEN) > 50

    def test_prompt_structure(self):
        """Тест структуры промпта"""
        assert "Stay tuned for updates" in TWITTER_PROMPT
        assert "@johndoe" in TWITTER_PROMPT
        assert "usernames of involved people" in TWITTER_PROMPT
