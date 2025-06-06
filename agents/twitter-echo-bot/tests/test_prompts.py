"""Модульные тесты для Twitter Echo Bot Prompts"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEchoBotPrompts:
    async def test_get_prompt_for_create_user_prompt(self):
        """Тест создания промпта для пользователя"""
        from twitter_echo_bot.config.promts import get_prompt_for_create_user_prompt

        words = "crypto-anarchist-chaotic"
        result = await get_prompt_for_create_user_prompt(words)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["role"] == "system"
        assert "crypto-anarchist-chaotic" in result[0]["content"]
        assert "Personality and Tone" in result[0]["content"]

    async def test_get_prompt_by_user_for_creating_tweet(self):
        """Тест создания промпта для твита"""
        from twitter_echo_bot.config.promts import get_prompt_by_user_for_creating_tweet

        user_prompt = "Be sarcastic and witty"
        text = "This is a test tweet"
        result = await get_prompt_by_user_for_creating_tweet(user_prompt, text)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["role"] == "system"
        assert user_prompt in result[0]["content"]
        assert text in result[0]["content"]

    async def test_prompts_structure(self):
        """Тест структуры промптов"""
        from twitter_echo_bot.config.promts import (
            get_prompt_by_user_for_creating_tweet,
            get_prompt_for_create_user_prompt,
        )

        result1 = await get_prompt_for_create_user_prompt("test-traits")
        assert all(key in result1[0] for key in ["role", "content"])

        result2 = await get_prompt_by_user_for_creating_tweet("test", "tweet")
        assert all(key in result2[0] for key in ["role", "content"])
