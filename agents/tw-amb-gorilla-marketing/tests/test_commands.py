"""Модульные тесты для Twitter Gorilla Marketing Agent"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["send_openai_request"] = MagicMock()
sys.modules["send_openai_request.main"] = MagicMock()
sys.modules["tweetscout_utils"] = MagicMock()
sys.modules["tweetscout_utils.main"] = MagicMock()

from tw_amb_gorilla_marketing.commands import PROMPT_FOR_CHECK, PROMPT_FOR_COMMENT, check_tweets_for_gorilla_marketing


class TestGorillaMarketingCommands:
    def test_prompt_constants(self):
        assert "True or False" in PROMPT_FOR_CHECK
        assert "Web3" in PROMPT_FOR_CHECK
        assert "AI" in PROMPT_FOR_CHECK
        assert "blockchain" in PROMPT_FOR_CHECK

    def test_comment_prompt_structure(self):
        assert "NFINITY" in PROMPT_FOR_COMMENT
        assert "AI Twitter Ambassador" in PROMPT_FOR_COMMENT
        assert "1-2 sentences" in PROMPT_FOR_COMMENT

    @patch("tw_amb_gorilla_marketing.commands.send_openai_request", new_callable=MagicMock)
    async def test_check_tweets_positive(self, mock_openai):
        # Создаем AsyncMock для корректной работы с await
        async def async_return(*args, **kwargs):
            return "True"

        mock_openai.side_effect = async_return

        mock_tweet = MagicMock()
        mock_tweet.full_text = "AI and blockchain are the future"

        result = await check_tweets_for_gorilla_marketing(
            tweets=[mock_tweet], keywords=["AI"], themes=["blockchain"], my_username="test_user"
        )

        assert len(result) == 1
        assert result[0] == mock_tweet

    def test_prompts_not_empty(self):
        assert len(PROMPT_FOR_CHECK) > 100
        assert len(PROMPT_FOR_COMMENT) > 100
        assert "Token prices" in PROMPT_FOR_CHECK
        assert "DONT USE HASHTAG" in PROMPT_FOR_COMMENT
