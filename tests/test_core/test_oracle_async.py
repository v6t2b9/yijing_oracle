# tests/test_core/test_oracle_async.py

import pytest
import asyncio
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from yijing.core.oracle import YijingOracle
from yijing.exceptions import (
    ModelConnectionError,
    ModelResponseError,
    ConfigurationError
)
from yijing.config import Settings
from yijing.enums import ModelType, ConsultationMode

# Fixtures für häufig verwendete Testdaten
@pytest.fixture
def mock_settings():
    settings = Settings()
    settings.model_type = ModelType.OLLAMA
    settings.active_model = "llama2:latest"
    settings.consultation_mode = ConsultationMode.SINGLE
    return settings

@pytest.fixture
def oracle(mock_settings):
    """Erzeugt eine Oracle-Instanz mit Mock-Einstellungen."""
    oracle = YijingOracle()
    oracle.settings = mock_settings
    oracle.model = AsyncMock()
    return oracle

@pytest.fixture
def mock_response():
    """Erzeugt eine Mock-Antwort für Modell-Responses."""
    response = MagicMock()
    response.text = "Test Antwort"
    return response

@pytest.fixture
async def mock_response():
    """Erzeugt eine Mock-Antwort für Modell-Responses."""
    response = MagicMock()
    response.text = "Test Antwort"
    response.parts = [MagicMock(text="Test Antwort")]
    return response


# Tests für GenAI-Modell-Interaktionen
@pytest.mark.asyncio
async def test_get_model_response_async_success(oracle, mock_response):
    """
    Testet erfolgreiche asynchrone Modellantwort.
    
    Dieser Test überprüft den Standardfall, bei dem das Modell
    erfolgreich eine Antwort generiert.
    """
    oracle.model.generate_content_async = AsyncMock(return_value=mock_response)
    
    result = await oracle._get_model_response_async("Test Prompt")
    
    assert result == "Test Antwort"
    oracle.model.generate_content_async.assert_called_once_with("Test Prompt")

@pytest.mark.asyncio
async def test_get_model_response_async_timeout(oracle):
    """
    Testet Zeitüberschreitung bei Modellanfragen.
    
    Dieser Test simuliert eine Zeitüberschreitung und überprüft,
    ob die korrekte Exception ausgelöst wird.
    """
    async def mock_timeout(*args, **kwargs):
        await asyncio.sleep(0.1)  # Kurze Verzögerung
        raise asyncio.TimeoutError()
        
    oracle.model.generate_content_async = AsyncMock(side_effect=mock_timeout)
    
    with pytest.raises(ModelConnectionError) as exc_info:
        await oracle._get_model_response_async("Test Prompt")
    
    assert "Wiederholte Zeitüberschreitungen" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_model_response_async_invalid_response(oracle):
    """
    Testet Behandlung ungültiger Modellantworten.
    
    Dieser Test überprüft, ob ungültige Antwortformate korrekt
    erkannt und behandelt werden.
    """
    invalid_response = MagicMock()
    delattr(invalid_response, 'text')  # Entferne text-Attribut
    
    oracle.model.generate_content_async = AsyncMock(return_value=invalid_response)
    
    with pytest.raises(ModelResponseError) as exc_info:
        await oracle._get_model_response_async("Test Prompt")
    
    assert "Keine gültige Antwort" in str(exc_info.value)


@pytest.mark.asyncio
async def test_chat_session_management(oracle):
    """
    Testet die Chat-Session-Verwaltung.
    
    Dieser Test überprüft die korrekte Initialisierung und
    Verwaltung von Chat-Sessions im Dialogue-Modus.
    """
    oracle.settings.consultation_mode = ConsultationMode.DIALOGUE
    oracle.chat_session = None
    
    # Mock für start_chat_async
    mock_session = AsyncMock()
    oracle.model.start_chat_async = AsyncMock(return_value=mock_session)
    
    await oracle._handle_chat_session_async()
    
    assert oracle.chat_session == mock_session
    oracle.model.start_chat_async.assert_called_once()

@pytest.mark.asyncio
async def test_chat_session_error_handling(oracle):
    """
    Testet Fehlerbehandlung bei Session-Initialisierung.
    
    Dieser Test überprüft, ob Fehler bei der Session-Initialisierung
    korrekt erkannt und behandelt werden.
    """
    oracle.settings.consultation_mode = ConsultationMode.DIALOGUE
    oracle.chat_session = None
    
    # Simuliere Fehler bei Session-Start
    oracle.model.start_chat_async = AsyncMock(
        side_effect=Exception("Session-Fehler")
    )
    
    with pytest.raises(ModelConnectionError) as exc_info:
        await oracle._handle_chat_session_async()
    
    assert "Chat-Session-Initialisierung fehlgeschlagen" in str(exc_info.value)

# Integrationstest für die Hauptfunktionalität
@pytest.mark.asyncio
async def test_get_response_async_integration(oracle, mock_response):
    """
    Integrationstest für die gesamte asynchrone Antwortgenerierung.
    
    Dieser Test überprüft den vollständigen Ablauf der asynchronen
    Antwortgenerierung, von der Hexagramm-Generierung bis zur
    Modellantwort.
    """
    # Mocks für alle benötigten Komponenten
    oracle.api_key = "test-api-key"
    oracle.settings.model_type = ModelType.GENAI
    oracle.model.generate_content_async = AsyncMock(return_value=mock_response)
    oracle._cast_hypergram_async = AsyncMock()
    oracle._create_hexagram_context_async = AsyncMock()
    oracle._generate_prompt_async = AsyncMock(return_value="Test Prompt")
    
    result = await oracle.get_response_async("Testfrage")
    
    assert isinstance(result, dict)
    assert 'answer' in result
    assert 'timestamp' in result
    assert isinstance(result['timestamp'], str)
    datetime.fromisoformat(result['timestamp'])  # Validiere Timestamp-Format