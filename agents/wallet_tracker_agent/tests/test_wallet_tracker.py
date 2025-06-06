"""Модульные тесты для Wallet Tracker Agent"""

import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["aiohttp"] = MagicMock()
sys.modules["aiogram"] = MagicMock()
sys.modules["aiogram.filters"] = MagicMock()
sys.modules["aiogram.types"] = MagicMock()
sys.modules["database"] = MagicMock()
sys.modules["database.redis"] = MagicMock()
sys.modules["database.redis.redis_client"] = MagicMock()


class TestWalletTracker(unittest.TestCase):
    def test_transaction_dataclass(self):
        """Тест создания dataclass Transaction"""
        from wallet_tracker import Transaction

        tx = Transaction(
            wallet="0x123", type="buy", token="ETH", amount=1.5, timestamp=1234567890, hash="0xabc123", chain="eth"
        )

        assert tx.wallet == "0x123"
        assert tx.type == "buy"
        assert tx.token == "ETH"
        assert tx.amount == 1.5
        assert tx.chain == "eth"

    def test_hex_to_decimal_with_hex(self):
        """Тест конвертации hex в decimal"""
        from wallet_tracker import hex_to_decimal

        result = hex_to_decimal("0x10", "value")
        assert result == 16.0

        result = hex_to_decimal("0xFF", "timestamp")
        assert result == 255

    def test_hex_to_decimal_without_hex(self):
        """Тест конвертации обычного числа"""
        from wallet_tracker import hex_to_decimal

        result = hex_to_decimal("100", "value")
        assert result == 100.0
