import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Dispatcher
from aiogram.types import Chat, Message, User

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apy_agent import main, setup_handlers


class TestTelegramBot:
    def setup_method(self):
        self.dp = Dispatcher()
        self.agent = MagicMock()
        setup_handlers(self.dp, self.agent)

    def create_message(self, text, user_id=123, username="testuser"):
        message = MagicMock(spec=Message)
        message.text = text
        message.from_user = MagicMock(spec=User)
        message.from_user.username = username
        message.from_user.id = user_id
        message.chat = MagicMock(spec=Chat)
        message.chat.id = 456
        message.answer = AsyncMock()
        message.reply = AsyncMock()
        return message

    @pytest.mark.asyncio
    async def test_start_command(self):
        message = self.create_message("/start")

        handlers = self.dp.message.handlers
        start_handler = None
        for handler in handlers:
            if hasattr(handler.callback, "__name__") and handler.callback.__name__ == "cmd_start":
                start_handler = handler.callback
                break

        assert start_handler is not None
        await start_handler(message)

        message.answer.assert_called_once()
        call_args = message.answer.call_args
        assert "Привет!" in call_args[0][0]
        assert call_args[1]["parse_mode"] == "Markdown"

    @pytest.mark.asyncio
    async def test_help_command(self):
        message = self.create_message("/help")

        handlers = self.dp.message.handlers
        help_handler = None
        for handler in handlers:
            if hasattr(handler.callback, "__name__") and handler.callback.__name__ == "cmd_help":
                help_handler = handler.callback
                break

        assert help_handler is not None
        await help_handler(message)

        # Help command should show the same message as start
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_pools_no_token_address(self):
        message = self.create_message("/find_pools")

        handlers = self.dp.message.handlers
        find_handler = None
        for handler in handlers:
            if hasattr(handler.callback, "__name__") and handler.callback.__name__ == "find_pools":
                find_handler = handler.callback
                break

        assert find_handler is not None
        await find_handler(message)

        message.answer.assert_called_once()
        call_args = message.answer.call_args
        assert "укажите адрес токена" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_find_pools_success(self):
        message = self.create_message("/find_pools 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
        status_msg = MagicMock()
        status_msg.edit_text = AsyncMock()
        message.answer.return_value = status_msg

        best_pool = {"protocol": "uniswap", "protocol_name": "Uniswap V3", "apy": 10, "found_pools": []}

        self.agent.find_best_pool = AsyncMock(return_value=best_pool)
        self.agent.format_investment_recommendation = MagicMock(return_value="Test recommendation")

        handlers = self.dp.message.handlers
        find_handler = None
        for handler in handlers:
            if hasattr(handler.callback, "__name__") and handler.callback.__name__ == "find_pools":
                find_handler = handler.callback
                break

        await find_handler(message)

        message.answer.assert_called_once_with("🔍 Ищу лучшие пулы для инвестирования...")
        self.agent.find_best_pool.assert_called_once_with("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
        status_msg.edit_text.assert_called_once_with("Test recommendation", parse_mode="Markdown")

    @pytest.mark.asyncio
    async def test_find_pools_exception(self):
        message = self.create_message("/find_pools 0x123")
        status_msg = MagicMock()
        status_msg.edit_text = AsyncMock()
        message.answer.return_value = status_msg

        self.agent.find_best_pool = AsyncMock(side_effect=Exception("Test error"))

        handlers = self.dp.message.handlers
        find_handler = None
        for handler in handlers:
            if hasattr(handler.callback, "__name__") and handler.callback.__name__ == "find_pools":
                find_handler = handler.callback
                break

        await find_handler(message)

        status_msg.edit_text.assert_called_once()
        error_call = status_msg.edit_text.call_args[0][0]
        assert "Произошла ошибка" in error_call
        assert "Test error" in error_call

    @pytest.mark.asyncio
    async def test_main_function(self):
        with patch("apy_agent.Bot") as mock_bot_class:
            with patch("apy_agent.Dispatcher") as mock_dp_class:
                with patch("apy_agent.APYAgent") as mock_agent_class:
                    with patch("apy_agent.setup_handlers") as mock_setup:
                        with patch("apy_agent.TELEGRAM_BOT_TOKEN", "test-token"):
                            with patch("apy_agent.ENSO_API_KEY", "test-key"):
                                mock_dp = AsyncMock()
                                mock_dp_class.return_value = mock_dp

                                # Run main but stop polling immediately
                                mock_dp.start_polling = AsyncMock(side_effect=KeyboardInterrupt())

                                try:
                                    await main()
                                except KeyboardInterrupt:
                                    pass

                                mock_bot_class.assert_called_once_with(token="test-token")
                                mock_agent_class.assert_called_once_with("test-key")
                                mock_setup.assert_called_once()
