"""Модульные тесты для Persona Agent"""

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем внешние зависимости
sys.modules["ray"] = MagicMock()
sys.modules["ray.serve"] = MagicMock()
sys.modules["base_agent"] = MagicMock()
sys.modules["base_agent.ray_entrypoint"] = MagicMock()
sys.modules["base_agent.prompt.utils"] = MagicMock()
sys.modules["qdrant_client_custom.main"] = MagicMock()
sys.modules["redis_client.main"] = MagicMock()
sys.modules["send_openai_request.main"] = MagicMock()

from persona_agent.ray_entrypoint import InputModel, OutputModel


class TestPersonaAgentModels:
    """Тесты для моделей Persona Agent"""

    def test_input_model_creation(self):
        """Тест создания InputModel"""
        input_data = InputModel(prompt="Generate a tweet about AI")
        assert input_data.prompt == "Generate a tweet about AI"

    def test_output_model_creation(self):
        """Тест создания OutputModel"""
        output_data = OutputModel(success=True, result="Generated tweet")
        assert output_data.success is True
        assert output_data.result == "Generated tweet"

    def test_output_model_failure(self):
        """Тест OutputModel для ошибки"""
        output_data = OutputModel(success=False, result="Error occurred")
        assert output_data.success is False

    def test_output_model_serialization(self):
        """Тест сериализации OutputModel"""
        output_data = OutputModel(success=True, result="Test result")
        serialized = output_data.model_dump()
        assert isinstance(serialized, dict)
        assert serialized["success"] is True

    def test_input_model_validation(self):
        """Тест валидации InputModel"""
        input_data = InputModel(prompt="Test prompt")
        assert isinstance(input_data.prompt, str)
        assert len(input_data.prompt) > 0
