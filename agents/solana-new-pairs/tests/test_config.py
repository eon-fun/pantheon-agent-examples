"""Модульные тесты для Solana New Pairs Agent"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["agents_tools_logger"] = MagicMock()
sys.modules["agents_tools_logger.main"] = MagicMock()

from solana_new_pairs.config.config import DBSettings, DexToolsSettings, FastAPISettings


class TestSolanaConfig:
    """Тесты для конфигурации Solana Agent"""

    def test_db_settings_defaults(self):
        """Тест настроек БД по умолчанию"""
        db_settings = DBSettings()
        assert db_settings.user == "postgres"
        assert db_settings.password == "password"
        assert db_settings.host == "localhost"

    def test_db_url_generation(self):
        """Тест генерации URL для БД"""
        db_settings = DBSettings()
        expected = "postgresql+asyncpg://postgres:password@localhost:5432/new_solana_pairs"
        assert expected in db_settings.url

    def test_fastapi_settings_defaults(self):
        """Тест настроек FastAPI по умолчанию"""
        fastapi_settings = FastAPISettings()
        assert "http://localhost:8080" in fastapi_settings.allowed_origins
        assert "POST" in fastapi_settings.allowed_methods

    def test_dextools_settings(self):
        """Тест настроек DexTools"""
        with patch.dict(os.environ, {"DEX_API_KEY": "test_key"}):
            dex_settings = DexToolsSettings()
            assert dex_settings.api_key == "test_key"
            assert dex_settings.plan == "trial"

    def test_fastapi_headers(self):
        """Тест заголовков FastAPI"""
        fastapi_settings = FastAPISettings()
        assert "Content-Type" in fastapi_settings.allowed_headers
        assert fastapi_settings.allowed_credentials is True
