"""Модульные тесты для Telegram Listener Agent"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram_listener.schemas import StoredMessage, TelegramMessageData, TelegramUser


class TestTelegramSchemas:
    """Тесты для схем Telegram Listener Agent"""

    def test_telegram_user_creation(self):
        """Тест создания TelegramUser"""
        user = TelegramUser(id=123456, is_bot=False, username="johndoe")
        assert user.id == 123456
        assert user.is_bot is False
        assert user.username == "johndoe"

    def test_telegram_user_minimal(self):
        """Тест создания TelegramUser с минимальными данными"""
        user = TelegramUser(id=123456, is_bot=True)
        assert user.id == 123456
        assert user.is_bot is True
        assert user.first_name is None

    def test_message_data_creation(self):
        """Тест создания TelegramMessageData"""
        user = TelegramUser(id=123456, is_bot=False)
        timestamp = datetime.now()
        message = TelegramMessageData(
            message_id=1, chat_id=-100123, sender=user, text="Hello!", timestamp=timestamp, raw_message={"id": 1}
        )
        assert message.message_id == 1
        assert message.text == "Hello!"

    def test_stored_message_creation(self):
        """Тест создания StoredMessage"""
        timestamp = datetime.now()
        stored_msg = StoredMessage(
            id=1,
            message_id=123,
            chat_id=-100123,
            user_id=123456,
            username="johndoe",
            text="Test",
            message_timestamp=timestamp,
        )
        assert stored_msg.id == 1
        assert stored_msg.username == "johndoe"
