"""Модульные тесты для Twitter Ambassador Posting Agent Commands"""

import os
import sys
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["redis_client"] = MagicMock()
sys.modules["redis_client.main"] = MagicMock()
sys.modules["send_openai_request"] = MagicMock()
sys.modules["send_openai_request.main"] = MagicMock()
sys.modules["send_openai_request.main"].send_openai_request = AsyncMock(return_value="Test text")
sys.modules["tweetscout_utils"] = MagicMock()
sys.modules["tweetscout_utils.main"] = MagicMock()
sys.modules["twitter_ambassador_utils"] = MagicMock()
sys.modules["twitter_ambassador_utils.main"] = MagicMock()


class TestPostingCommands:
    def test_prompt_constants(self):
        """Тест проверки констант промптов"""
        from twitter_ambassador_posting_agent.commands import (
            PROMPT_FOR_NEWS_TWEET,
            PROMPT_FOR_QUOTED_TWEET,
            PROMPT_FOR_TWEET,
        )

        assert "DONT USE HASHTAG" in PROMPT_FOR_TWEET
        assert "autonomous AI Twitter Ambassador" in PROMPT_FOR_TWEET
        assert "Maximum 260 characters" in PROMPT_FOR_TWEET

        assert "COMMENT THIS TWEET" in PROMPT_FOR_QUOTED_TWEET
        assert "bullish, positive" in PROMPT_FOR_QUOTED_TWEET

        assert "technology and innovation" in PROMPT_FOR_NEWS_TWEET
        assert "NFINITY" in PROMPT_FOR_NEWS_TWEET

    async def test_add_blank_lines(self):
        """Тест функции добавления пустых строк"""
        from send_openai_request.main import send_openai_request
        from twitter_ambassador_posting_agent.commands import add_blank_lines

        send_openai_request.side_effect = AsyncMock(return_value="Test text")
        result = await add_blank_lines("Test text")
        assert result == "Test text"

    async def test_format_text(self):
        """Тест функции форматирования текста"""
        from send_openai_request.main import send_openai_request
        from twitter_ambassador_posting_agent.commands import format_text

        send_openai_request.side_effect = AsyncMock(return_value="Short text")
        result = await format_text("Test text")
        assert len(result) <= 280
