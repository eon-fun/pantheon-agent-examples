"""Модульные тесты для Twitter Summary Prompts"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTwitterSummaryPrompts:
    def test_ai_prompt_structure(self):
        """Тест структуры AI промпта"""
        from prompts import AI_PROMPT

        assert isinstance(AI_PROMPT, str)
        assert len(AI_PROMPT) > 100
        assert "social media analyst" in AI_PROMPT
        assert "cryptocurrency" in AI_PROMPT
        assert "celebrity news" in AI_PROMPT

    def test_ai_prompt_instructions(self):
        """Тест инструкций в AI промпте"""
        from prompts import AI_PROMPT

        # Проверяем ключевые инструкции
        assert "Combine related tweets" in AI_PROMPT
        assert "main events or announcements" in AI_PROMPT
        assert "possible implications" in AI_PROMPT
        assert "Include usernames" in AI_PROMPT
        assert "HTML formatting" in AI_PROMPT

    def test_ai_prompt_examples(self):
        """Тест примеров в AI промпте"""
        from prompts import AI_PROMPT

        # Проверяем примеры форматирования
        assert "@johndoe" in AI_PROMPT
        assert "Stay tuned for updates! 🚀" in AI_PROMPT
        assert "Famous investor John Doe" in AI_PROMPT
        assert "This could lead to increased confidence" in AI_PROMPT

    def test_ai_prompt_language_requirements(self):
        """Тест требований к языку"""
        from prompts import AI_PROMPT

        assert "English" in AI_PROMPT
        assert "Telegram posts" in AI_PROMPT
        assert "engaging and clear language" in AI_PROMPT
