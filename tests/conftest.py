 tests/conftest.py

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

@pytest.fixture(scope="function")
def mock_oracle_environment(test_resources_dir):
    """Setzt eine kontrollierte Testumgebung für das Oracle auf."""
    env_vars = {
        "GENAI_API_KEY": "test-api-key",
        "OLLAMA_HOST": "http://test-host",
        "DEBUG": "True",
        "LOG_LEVEL": "DEBUG"
    }
    
    # Backup der existierenden Umgebungsvariablen
    old_env = {}
    for key in env_vars:
        old_env[key] = os.environ.get(key)
        os.environ[key] = env_vars[key]
    
    yield env_vars
    
    # Stelle ursprüngliche Umgebung wieder her
    for key, value in old_env.items():
        if value is None:
            del os.environ[key]
        else:
            os.environ[key] = value
