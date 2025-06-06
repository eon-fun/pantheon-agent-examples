"""Модульные тесты для Twitter Mention Answerer Agent"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["send_openai_request"] = MagicMock()
sys.modules["send_openai_request.main"] = MagicMock()

from tw_amb_mention_answerer.commands import (
    PROMPT_CHECK_MENTION_REPLY,
    PROMPT_FOR_MENTION_REPLY,
    check_mention_needs_reply,
)


class TestMentionAnswererCommands:
    def test_prompt_constants(self):
        assert "technology community manager" in PROMPT_FOR_MENTION_REPLY
        assert "Twitter mentions" in PROMPT_FOR_MENTION_REPLY
        assert "Twitter Ambassador" in PROMPT_FOR_MENTION_REPLY

    def test_check_prompt_structure(self):
        assert "AI community manager" in PROMPT_CHECK_MENTION_REPLY
        assert "True or False" in PROMPT_CHECK_MENTION_REPLY
        assert "Spam or promotional content" in PROMPT_CHECK_MENTION_REPLY

    @patch("tw_amb_mention_answerer.commands.send_openai_request")
    async def test_check_mention_needs_reply_true(self, mock_openai):
        async def async_return(*args, **kwargs):
            return "True"

        mock_openai.side_effect = async_return
        result = await check_mention_needs_reply(
            mention_text="Hi @user, what do you think about AI?", my_username="user"
        )
        assert result is True

    @patch("tw_amb_mention_answerer.commands.send_openai_request")
    async def test_check_mention_needs_reply_false(self, mock_openai):
        async def async_return(*args, **kwargs):
            return "False"

        mock_openai.side_effect = async_return
        result = await check_mention_needs_reply(mention_text="Spam content @user", my_username="user")
        assert result is False

    def test_prompt_lengths(self):
        assert len(PROMPT_FOR_MENTION_REPLY) > 200
        assert len(PROMPT_CHECK_MENTION_REPLY) > 100
