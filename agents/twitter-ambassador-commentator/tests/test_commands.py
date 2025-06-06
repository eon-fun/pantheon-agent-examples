"""Модульные тесты для Twitter Ambassador Commentator Agent"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["send_openai_request"] = MagicMock()
sys.modules["send_openai_request.main"] = MagicMock()

from twitter_ambassador_commentator.commands import PROMPT, create_comment_to_post


class TestCommentatorCommands:
    def test_prompt_constants(self):
        assert "AI and crypto enthusiast" in PROMPT
        assert "NFINITY" in PROMPT
        assert "Twitter Ambassador" in PROMPT
        assert "DONT USE HASHTAG" in PROMPT

    def test_prompt_structure(self):
        assert "Max length of comment is 1 sentence" in PROMPT
        assert "positive, bullish" in PROMPT
        assert "human-like as possible" in PROMPT

    def test_prompt_guidelines(self):
        assert "Be Positive" in PROMPT
        assert "Conciseness" in PROMPT
        assert "No Rocket Emoji" in PROMPT

    @patch("twitter_ambassador_commentator.commands.send_openai_request")
    @patch("twitter_ambassador_commentator.commands.format_text")
    async def test_create_comment_to_post(self, mock_format, mock_openai):
        async def async_openai_return(*args, **kwargs):
            return "Great point about AI!"

        async def async_format_return(*args, **kwargs):
            return "Great point about AI!"

        mock_openai.side_effect = async_openai_return
        mock_format.side_effect = async_format_return

        result = await create_comment_to_post(twitter_post="AI is the future", my_username="test_user")

        assert result == "Great point about AI!"

    def test_prompt_length(self):
        assert len(PROMPT) > 300
