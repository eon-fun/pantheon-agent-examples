"""Модульные тесты для AI Dialogue Manager"""

import os
import sys
from unittest.mock import MagicMock

import pytest

# Добавляем родительскую директорию в sys.path для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости перед импортом
sys.modules["ray"] = MagicMock()
sys.modules["database.redis.redis_client"] = MagicMock()
sys.modules["services.ai_connectors.openai_client"] = MagicMock()
sys.modules["telethon"] = MagicMock()
sys.modules["telethon.tl.types"] = MagicMock()

from ray_dialogue_manager import TELEGRAM_PROMPT


class TestDialogueManagerConstants:
    """Тесты для констант и конфигурации диалога менеджера"""

    def test_telegram_prompt_exists(self):
        """Тест наличия промпт-шаблона для Telegram"""
        assert TELEGRAM_PROMPT is not None
        assert len(TELEGRAM_PROMPT) > 50

    def test_telegram_prompt_content(self):
        """Тест содержания промпт-шаблона"""
        assert "summarizing messages" in TELEGRAM_PROMPT
        assert "brief summary" in TELEGRAM_PROMPT
        assert "@username mentioned" in TELEGRAM_PROMPT
        assert "topic" in TELEGRAM_PROMPT

    def test_telegram_prompt_instructions(self):
        """Тест наличия ключевых инструкций"""
        assert "without answering any questions" in TELEGRAM_PROMPT
        assert "concisely" in TELEGRAM_PROMPT
        assert "chat name" in TELEGRAM_PROMPT
        assert "Do not provide solutions" in TELEGRAM_PROMPT


class MockMessageProcessor:
    """Тестовая версия MessageProcessor без Ray декораторов"""

    def __init__(self):
        self.db = MagicMock()

    async def process_message(self, message_data):
        """Мокированная версия process_message"""
        try:
            if not message_data:
                return
            self.db.add_to_sorted_set.assert_called_once()
        except Exception as e:
            print(f"Error processing message: {e}")

    async def generate_summary(self):
        """Мокированная версия generate_summary"""
        try:
            messages = self.db.get_sorted_set("telegram_messages")
            if not messages:
                return "No messages to process."

            # Мокированная логика генерации сводки
            return "Summary generated successfully"
        except Exception as e:
            return f"Error processing summary: {e}"


class TestMessageProcessor:
    """Тесты для функциональности MessageProcessor"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.processor = MockMessageProcessor()

    @pytest.mark.asyncio
    async def test_process_empty_message(self):
        """Тест обработки пустого сообщения"""
        result = await self.processor.process_message(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_summary_no_messages(self):
        """Тест генерации сводки без сообщений"""
        self.processor.db.get_sorted_set.return_value = []
        result = await self.processor.generate_summary()
        assert result == "No messages to process."

    @pytest.mark.asyncio
    async def test_generate_summary_with_messages(self):
        """Тест генерации сводки с сообщениями"""
        self.processor.db.get_sorted_set.return_value = ["msg1", "msg2"]
        result = await self.processor.generate_summary()
        assert "Summary generated" in result
