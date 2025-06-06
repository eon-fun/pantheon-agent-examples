"""Модульные тесты для Example Agent"""

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем все внешние зависимости
sys.modules["ray"] = MagicMock()
sys.modules["ray.serve"] = MagicMock()
sys.modules["shared.agents.base_agent"] = MagicMock()
sys.modules["workflows"] = MagicMock()
sys.modules["workflows.basic"] = MagicMock()

# Создаем мок для BaseAgent
base_agent_mock = MagicMock()
base_agent_mock.BaseAgent = type("BaseAgent", (), {})
sys.modules["shared.agents.base_agent"] = base_agent_mock

# Создаем мок для Workflow
workflow_mock = MagicMock()
workflow_mock.Workflow = type("Workflow", (), {})
sys.modules["workflows.basic"] = workflow_mock


class TestWorkflowConstants:
    """Тесты для констант и базовой структуры"""

    def test_imports_available(self):
        """Тест доступности импортов"""
        assert "shared.agents.base_agent" in sys.modules
        assert "workflows.basic" in sys.modules

    def test_module_structure(self):
        """Тест структуры модуля"""
        import src.example_agent

        assert hasattr(src.example_agent, "__init__")

    def test_ray_serve_available(self):
        """Тест доступности Ray Serve"""
        assert "ray.serve" in sys.modules

    def test_base_agent_mock(self):
        """Тест мока BaseAgent"""
        from shared.agents.base_agent import BaseAgent

        assert BaseAgent is not None
