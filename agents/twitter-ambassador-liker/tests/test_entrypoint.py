"""Модульные тесты для Twitter Ambassador Liker Agent"""

import os
import re
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["ray"] = MagicMock()
sys.modules["base_agent"] = MagicMock()
sys.modules["base_agent.ray_entrypoint"] = MagicMock()
sys.modules["redis_client"] = MagicMock()
sys.modules["redis_client.main"] = MagicMock()
sys.modules["tweetscout_utils"] = MagicMock()
sys.modules["tweetscout_utils.main"] = MagicMock()
sys.modules["twitter_ambassador_utils"] = MagicMock()
sys.modules["twitter_ambassador_utils.main"] = MagicMock()


class TestLikerAgent:
    def test_regex_patterns(self):
        """Тест регулярных выражений для парсинга goal"""
        goal = "testuser.keyword1,keyword2.theme1,theme2"
        parts = goal.split(".")
        my_username = parts[0]
        keywords = re.findall(r"[a-zA-Z0-9]+", parts[1])
        themes = re.findall(r"[a-zA-Z0-9]+", parts[2])

        assert my_username == "testuser"
        assert keywords == ["keyword1", "keyword2"]
        assert themes == ["theme1", "theme2"]

    def test_parsing_and_special_chars(self):
        """Тест парсинга и обработки спецсимволов"""
        goal = "user.ai.blockchain"
        parts = goal.split(".")
        assert len(parts) == 3

        keywords_string = "ai,blockchain,crypto"
        keywords = re.findall(r"[a-zA-Z0-9]+", keywords_string)
        assert keywords == ["ai", "blockchain", "crypto"]

        # Тест спецсимволов
        special_string = "ai-ml,web3.0,#crypto"
        special_keywords = re.findall(r"[a-zA-Z0-9]+", special_string)
        assert special_keywords == ["ai", "ml", "web3", "0", "crypto"]

    def test_entrypoint_imports(self):
        """Тест импорта модуля entrypoint с мокированием зависимостей"""
        import twitter_ambassador_liker.entrypoint

        assert twitter_ambassador_liker.entrypoint is not None
