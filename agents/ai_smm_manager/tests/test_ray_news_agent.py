"""Модульные тесты для AI SMM Manager - Константы"""

import os
import sys
from unittest.mock import MagicMock

# Добавляем родительскую директорию в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["ray"] = MagicMock()
sys.modules["aiohttp"] = MagicMock()
sys.modules["bs4"] = MagicMock()
sys.modules["database.redis.redis_client"] = MagicMock()
sys.modules["services.ai_connectors.openai_client"] = MagicMock()

from ray_news_agent import PROMPT


class TestNewsAgentConstants:
    """Тесты для констант и конфигурации"""

    def test_prompt_exists(self):
        """Тест наличия промпт-шаблона"""
        assert PROMPT is not None
        assert len(PROMPT) > 50
        assert "Telegram post author" in PROMPT

    def test_prompt_content(self):
        """Тест содержания промпт-шаблона"""
        assert "cryptocurrency news channel" in PROMPT
        assert "Markdown formatting" in PROMPT
        assert "hashtags" in PROMPT
        assert "emojis" in PROMPT

    def test_prompt_formatting_instructions(self):
        """Тест инструкций по форматированию"""
        assert "bold formatting" in PROMPT
        assert "italic for emphasis" in PROMPT
        assert "Stay tuned for more updates" in PROMPT

    def test_prompt_structure(self):
        """Тест структуры промпта"""
        lines = PROMPT.strip().split("\n")
        assert len(lines) > 3
        assert any("You are" in line for line in lines)
        assert any("Write concise" in line for line in lines)
