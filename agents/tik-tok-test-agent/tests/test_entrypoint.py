"""Модульные тесты для TikTok Test Agent"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["ray"] = MagicMock()
sys.modules["base_agent"] = MagicMock()
sys.modules["base_agent.ray_entrypoint"] = MagicMock()
sys.modules["tik_tok_package"] = MagicMock()
sys.modules["tik_tok_package.main"] = MagicMock()

from tik_tok_test_agent.entrypoint import get_agent, install_chrome_linux


class TestTikTokAgent:
    """Тесты для TikTok Test Agent"""

    @patch("subprocess.run")
    def test_install_chrome_linux(self, mock_subprocess):
        """Тест установки Chrome на Linux"""
        mock_subprocess.return_value.returncode = 0
        result = install_chrome_linux()
        assert mock_subprocess.call_count >= 2
        assert result is not None

    def test_get_agent_function(self):
        """Тест функции get_agent"""
        agent_args = {"test": "value"}
        result = get_agent(agent_args)
        assert result is not None

    def test_environment_variables(self):
        """Тест переменных окружения"""
        with patch.dict(os.environ, {"TIKTOK_USERNAME": "test_user"}):
            username = os.getenv("TIKTOK_USERNAME")
            assert username == "test_user"

    def test_fastapi_app_exists(self):
        """Тест существования FastAPI приложения"""
        from tik_tok_test_agent.entrypoint import app

        assert app is not None

    @patch("tik_tok_test_agent.entrypoint.TikTokBot")
    def test_tiktok_bot_import(self, mock_tiktok_bot):
        """Тест импорта TikTokBot"""
        from tik_tok_test_agent.entrypoint import TikTokBot

        assert TikTokBot is not None
