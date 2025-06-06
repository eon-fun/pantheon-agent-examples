"""Модульные тесты для Ray Avatar Agent"""

import os
import sys
from unittest.mock import MagicMock

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости перед импортом
sys.modules["ray"] = MagicMock()
sys.modules["database.redis.redis_client"] = MagicMock()
sys.modules["services.ai_connectors.openai_client"] = MagicMock()

from ray_avatar import OPENAI_PROMPT_TEMPLATE


class TestAvatarConstants:
    """Тесты для констант и конфигурации"""

    def test_prompt_template_exists(self):
        """Тест наличия промпт-шаблона"""
        assert OPENAI_PROMPT_TEMPLATE is not None
        assert len(OPENAI_PROMPT_TEMPLATE) > 100

    def test_prompt_template_content(self):
        """Тест содержания промпт-шаблона"""
        assert "AI avatar" in OPENAI_PROMPT_TEMPLATE
        assert "friendly tone" in OPENAI_PROMPT_TEMPLATE
        assert "natural language" in OPENAI_PROMPT_TEMPLATE
        assert "politeness and professionalism" in OPENAI_PROMPT_TEMPLATE

    def test_prompt_template_guidelines(self):
        """Тест наличия руководящих принципов"""
        assert "1. Maintain politeness" in OPENAI_PROMPT_TEMPLATE
        assert "2. Adapt your tone" in OPENAI_PROMPT_TEMPLATE
        assert "3. Reference the last response" in OPENAI_PROMPT_TEMPLATE

    def test_prompt_template_structure(self):
        """Тест структуры промпта"""
        assert "Key guidelines:" in OPENAI_PROMPT_TEMPLATE
        assert "\n" in OPENAI_PROMPT_TEMPLATE  # многострочный
        assert len(OPENAI_PROMPT_TEMPLATE.split("\n")) > 5  # несколько строк
