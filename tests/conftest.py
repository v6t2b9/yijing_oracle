# tests/conftest.py

"""
Test Configuration and Fixtures
=============================
Provides shared test fixtures and configuration for the test suite.
"""

import pytest
import os
from pathlib import Path
from yijing.config import Settings
from yijing.models import Hexagram, HypergramLine
from yijing.enums import ModelType, ConsultationMode

@pytest.fixture(scope="session")
def test_resources_dir():
    """Erstellt ein temporäres Ressourcenverzeichnis für Tests."""
    test_dir = Path(__file__).parent / "test_resources"
    test_dir.mkdir(exist_ok=True)
    return test_dir

@pytest.fixture(scope="session")
def test_hexagram_data(test_resources_dir):
    """Erstellt Testdaten für Hexagramme."""
    hexagram_dir = test_resources_dir / "hexagram_json"
    hexagram_dir.mkdir(exist_ok=True)
    
    test_data = {
        "hexagram": {
            "name": "TEST_HEXAGRAM",
            "subtitle": "Test Subtitle",
            "trigrams": {
                "above": {"name": "Test", "attributes": "test"},
                "below": {"name": "Test", "attributes": "test"}
            },
            "meaning": {
                "description": "Test meaning",
                "season": "Test season"
            }
        },
        "judgment": {
            "description": "Test judgment",
            "analysis": ["Test analysis"]
        },
        "image": {
            "description": "Test image",
            "lesson": "Test lesson",
            "warning": "Test warning"
        },
        "lines": [
            {
                "position": f"Position {i}",
                "text": f"Text {i}",
                "interpretation": f"Interpretation {i}"
            }
            for i in range(1, 7)
        ]
    }
    
    # Speichere Testdaten als JSON
    test_file = hexagram_dir / "hexagram_01.json"
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    return test_data

# tests/conftest.py

@pytest.fixture
async def oracle(mock_oracle_environment):
    """Erzeugt eine Oracle-Testinstanz mit Mock-Einstellungen."""
    custom_settings = {
        "model_type": ModelType.GENAI,
        "active_model": "test-model",
        "consultation_mode": ConsultationMode.SINGLE,
        # Mock-API-Key für Tests
        "api_key": "test-api-key"
    }
    
    oracle = YijingOracle(
        api_key="test-api-key",
        custom_settings=custom_settings
    )
    oracle.model = AsyncMock()  # Mock das Modell für Tests
    return oracle