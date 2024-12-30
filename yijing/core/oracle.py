# yijing/core/oracle.py

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import google.generativeai as genai
import logging
import os
import json
import ollama  # Importieren Sie Ollama

from ..models import HypergramData, HexagramContext, HypergramLine, Hypergram
from .generator import cast_hypergram
from .manager import HexagramManager
from ..enums import ConsultationMode
from ..config import Settings, settings, ModelType
from ..utils.resource_loader import load_yijing_text, load_system_prompt

import aiohttp
import json
#from typing import Dict, Any, Optional

import asyncio
from datetime import datetime
from .exceptions import (
    ModelConnectionError,
    ModelResponseError,
    ResourceNotFoundError,
    HexagramTransformationError,
    ConfigurationError
)

# Verzeichnisse initialisieren
project_dir = Path.cwd() # Aktuelles Arbeitsverzeichnis
resources_dir = project_dir / 'yijing' / 'resources' # Ressourcenverzeichnis

@dataclass # Datenklasse für Oracle-Einstellungen
class OracleSettings: # Klasse für Oracle-Einstellungen
    """Settings for the Yijing Oracle."""
    system_prompt: Optional[str] = None # System-Prompt
    yijing_text: Optional[str] = None # Yijing-Text
    active_model: str = "models/gemini-1.5-flash" # Aktives Modell
    consultation_mode: ConsultationMode = ConsultationMode.SINGLE # Beratungsmodus

    def __post_init__(self):
        """
        Post-initialization method to load system prompt and Yijing text.

        This method loads the system prompt and Yijing text if they are not provided.
        """
        # Load the mode-specific system prompt if not provided
        if self.system_prompt is None: # Wenn System-Prompt nicht vorhanden
            self.system_prompt = load_system_prompt(self.consultation_mode) # System-Prompt laden
        
        # Load Yijing text if not provided
        if self.yijing_text is None: # Wenn Yijing-Text nicht vorhanden
            self.yijing_text = load_yijing_text() # Yijing-Text laden
        
        # Combine system prompt with Yijing text
        self.system_prompt = f"""{self.system_prompt}

Yijing Text Reference:
{self.yijing_text}
"""
    
    @classmethod
    def from_json(cls, path: Path) -> 'OracleSettings':
        """
        Load settings from a JSON file.

        Args:
            path (Path): The path to the JSON file containing the settings.

        Returns:
            OracleSettings: An instance of OracleSettings populated with data from the JSON file.
        """
        """Load settings from JSON file"""
        with open(path) as f:
            data = json.load(f)
        return cls(**data)

class YijingOracle:
    """
    The Yijing Oracle class for generating hexagram readings and responses.

    Args:
        api_key (str, optional): The API key for the Generative AI model. Defaults to None.
        resources_path (Path, optional): The path to the resources directory. Defaults to None.
        custom_settings (Dict[str, Any], optional): Custom settings to override the default settings. Defaults to None.

    Attributes:
        settings (Settings): The settings for the oracle.
        logger (Logger): The logger for the oracle.
        api_key (str): The API key for the Generative AI model.
        resources_path (Path): The path to the resources directory.
        hexagram_manager (HexagramManager): The hexagram manager for generating hexagram readings.
        model (GenerativeModel): The generative model used for generating responses.
        chat_session (ChatSession): The chat session for dialogue

    Raises:
        ValueError: If the API key is not provided for the GenAI model.
        FileNotFoundError: If required resource files are not found.
        RuntimeError: If an error occurs during initialization.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None, # API-Schlüssel
        resources_path: Optional[Path] = None, # Pfad zu den Ressourcen
        custom_settings: Optional[Dict[str, Any]] = None # Benutzerdefinierte Einstellungen
    ):
        # Initialize settings first
        self.settings = self._initialize_settings(custom_settings) # Einstellungen initialisieren
        self.logger = self._setup_logging() # Logging initialisieren
        
        # API key setup for GenAI
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") # API-Schlüssel
        if self.settings.model_type == ModelType.GENAI and not self.api_key: # Wenn GenAI verwendet wird und kein API-Schlüssel vorhanden ist
            raise ValueError(
                "API Schlüssel nicht gefunden. Bitte stellen Sie sicher, dass der API-Schlüssel bereitgestellt wird, "
                "entweder über einen Parameter oder die Umgebungsvariable 'GEMINI_API_KEY'."
            )
        
        # Configure GenAI if GenAI is used
        if self.settings.model_type == ModelType.GENAI: # Wenn GenAI verwendet wird
            genai.configure(api_key=self.api_key) # GenAI konfigurieren
        
        # Resources setup
        self.resources_path = resources_path or Path(__file__).parent.parent / 'resources' # Pfad zu den Ressourcen ist das Verzeichnis 'resources' im übergeordneten Verzeichnis
        self._verify_resource_structure() # Ressourcenstruktur überprüfen
        
        # Initialize hexagram manager
        self.hexagram_manager = HexagramManager(self.resources_path) # Hexagramm-Manager initialisieren
        
        # Set up GenAI or Ollama
        try:
            if self.settings.model_type == ModelType.GENAI:
                self.model = genai.GenerativeModel(
                    model_name=self.settings.active_model,
                    system_instruction=self._get_system_prompt()
                )
                
                # Initialize chat session for dialogue mode
                self.chat_session = None
                if self.settings.consultation_mode == ConsultationMode.DIALOGUE:
                    self.chat_session = self.model.start_chat()
            elif self.settings.model_type == ModelType.OLLAMA:
                # Keine spezifische Initialisierung für Ollama erforderlich
                pass
            else:
                raise ValueError(f"Unbekannter Modelltyp: {self.settings.model_type}")
                
        except Exception as e:
            self.logger.error("Fehler bei der Initialisierung", exc_info=True)
            raise RuntimeError(f"Oracle-Initialisierungsfehler: {str(e)}")
        
    def _initialize_settings(self, custom_settings: Optional[Dict[str, Any]] = None) -> Settings:
        """Initialize settings with either custom values or defaults."""
        if custom_settings:
            return Settings(**custom_settings)
        return settings

    def _ensure_resource_structure(self) -> None:
        """Create required resource directories if they don't exist."""
        directories = [
            self.resources_path,
            self.resources_path / 'hexagram_json',
            self.resources_path / 'schemas'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Ensured directory exists: {directory}")
            
    def _verify_resource_structure(self) -> None:
        """Verify that all required resource files exist."""
        required_files = [
            'consultation_template.txt',
            'system_prompt.txt'
        ]
        
        for file in required_files:
            file_path = self.resources_path / file
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Required resource file not found: {file_path}"
                )
            
    def _get_system_prompt(self) -> str:
        """
        Retrieve the appropriate system prompt based on consultation mode.

        Returns:
            str: The system prompt text.
        Raises:
            FileNotFoundError: If the system prompt file is not found.
        """
        try:
            # Korrigierter Pfad: Verwende das resources_path aus den Settings
            template_path = self.resources_path / 'consultation_template.txt'
            if not template_path.exists():
                raise FileNotFoundError(f"Consultation template not found at {template_path}")
                
            with open(template_path, 'r', encoding='utf-8') as f:
                consultation_template = f.read()
                
            system_prompt_path = self.resources_path / 'system_prompt.txt'
            if not system_prompt_path.exists():
                raise FileNotFoundError(f"System prompt not found at {system_prompt_path}")
                
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
                
            return f"{system_prompt}\n\n{consultation_template}"
                
        except Exception as e:
            self.logger.error(f"Error loading system prompt: {str(e)}")
            raise

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG if self.settings.debug else logging.INFO)
        return logger

    def get_response(self, question: str) -> Dict[str, Any]:
        """
        Generiert eine Weissagung basierend auf der Frage und dem gewählten Modell.
        
        Args:
            question (str): Die Frage an das Orakel
            
        Returns:
            Dict[str, Any]: Ein Dictionary mit der Weissagung und zusätzlichen Informationen
            
        Raises:
            ModelConnectionError: Wenn keine Verbindung zum KI-Modell hergestellt werden kann
            ModelResponseError: Wenn die Antwort des Modells ungültig ist
            ResourceNotFoundError: Wenn erforderliche Ressourcen nicht gefunden werden
            HexagramTransformationError: Wenn bei der Hexagramm-Transformation ein Fehler auftritt
            ConfigurationError: Wenn die Konfiguration ungültig ist
        """
        try:
            self.logger.info(
                f"Verarbeite Frage im {self.settings.consultation_mode} Modus "
                f"mit Modell {self.settings.model_type.value}"
            )
            
            # Validiere die Konfiguration
            self._validate_configuration()
            
            # Generiere Hexagrammdaten
            try:
                hypergram_data = cast_hypergram()
            except ValueError as e:
                raise HexagramTransformationError(
                    error_detail=str(e)
                ) from e
            
            # Erstelle Hexagrammkontext
            try:
                context = self._create_hexagram_context(hypergram_data)
            except FileNotFoundError as e:
                raise ResourceNotFoundError(
                    resource_path=str(e)
                ) from e
            
            # Generiere Beratungs-Prompt
            prompt = self.hexagram_manager.get_consultation_prompt(
                context=context,
                question=question
            )
            
            # Hole Modellantwort
            try:
                if self.settings.model_type == ModelType.GENAI:
                    response_text = self._get_model_response(prompt)
                else:
                    response_text = self._get_ollama_response(prompt)
            except ConnectionError as e:
                raise ModelConnectionError(
                    model_name=self.settings.active_model,
                    details=str(e)
                ) from e
            except Exception as e:
                raise ModelResponseError(
                    model_name=self.settings.active_model,
                    response=str(e)
                ) from e
                
            # Erstelle und validiere die Antwort
            response = {
                'answer': response_text,
                'hypergram_data': hypergram_data.dict(),
                'hexagram_context': {
                    'original': context.original_hexagram['hexagram']['name'],
                    'resulting': context.resulting_hexagram['hexagram']['name'],
                    'changing_lines': context.changing_lines
                },
                'model_used': self.settings.active_model,
                'timestamp': datetime.now().isoformat(),
                'consultation_mode': self.settings.consultation_mode
            }
            
            self._validate_response(response)
            return response
                
        except Exception as e:
            self.logger.error(
                "Unerwarteter Fehler bei der Generierung der Antwort",
                exc_info=True
            )
            raise
            
    def _validate_configuration(self) -> None:
        """
        Überprüft die Gültigkeit der Konfiguration.
        
        Raises:
            ConfigurationError: Wenn die Konfiguration ungültig ist
        """
        if self.settings.model_type == ModelType.GENAI and not self.api_key:
            raise ConfigurationError(
                "API-Schlüssel fehlt für GenAI-Modell"
            )
            
        if not self.resources_path.exists():
            raise ConfigurationError(
                f"Ressourcen-Verzeichnis nicht gefunden: {self.resources_path}"
            )
            
    def _validate_response(self, response: Dict[str, Any]) -> None:
        """
        Überprüft die Gültigkeit der generierten Antwort.
        
        Args:
            response (Dict[str, Any]): Die zu validierende Antwort
            
        Raises:
            ModelResponseError: Wenn die Antwort ungültig ist
        """
        required_keys = {'answer', 'hypergram_data', 'hexagram_context'}
        missing_keys = required_keys - set(response.keys())
        
        if missing_keys:
            raise ModelResponseError(
                model_name=self.settings.active_model,
                response=f"Fehlende Schlüssel in der Antwort: {missing_keys}"
            )
            
        if not isinstance(response['answer'], str) or not response['answer'].strip():
            raise ModelResponseError(
                model_name=self.settings.active_model,
                response="Leere oder ungültige Textantwort"
            )
        
    def _create_hexagram_context(self, hypergram_data: HypergramData) -> HexagramContext:
        """
        Create a hexagram context from hypergram data.
        Args:
            hypergram_data (HypergramData): The data containing the old and new hexagrams and the changing lines.
        Returns:
            HexagramContext: The context for the hexagram reading, including the original hexagram number, 
                             the changing lines, and the resulting hexagram number.
        """
        original_number = hypergram_data.old_hexagram.to_binary_number() + 1
        resulting_number = hypergram_data.new_hexagram.to_binary_number() + 1
        
        return self.hexagram_manager.create_reading_context(
            original_hex_num=original_number,
            changing_lines=hypergram_data.changing_lines,
            resulting_hex_num=resulting_number
        )

    def _get_single_response(self, prompt: str) -> str:
        """
        Generate a single response based on the provided prompt.
        Args:
            prompt (str): The input prompt to generate a response for.
        Returns:
            str: The generated response text.
        Raises:
            ValueError: If no valid response is received or the response does not have a 'text' attribute.
        """
        self.logger.debug("Generating single response")
        response = self.model.generate_content(prompt)
        
        if not response or not hasattr(response, 'text'):
            raise ValueError("No valid response received in single mode")
        
        return response.text

    def _get_dialogue_response(self, prompt: str) -> str:
        """
        Generate a response using the chat session.
        This method sends a prompt to the chat session and retrieves the response.
        If the chat session is not already started, it initializes a new session.
        Args:
            prompt (str): The input prompt to send to the chat session.
        Returns:
            str: The text of the first part of the response from the chat session.
        Raises:
            ValueError: If no valid response is received from the chat session.
        """
        self.logger.debug("Generating dialogue response")
        if not self.chat_session:
            self.chat_session = self.model.start_chat()
            
        response = self.chat_session.send_message(prompt)
        
        if not response or not hasattr(response, 'parts'):
            raise ValueError("No valid response received in dialogue mode")
            
        return response.parts[0].text

    def start_new_consultation(self):
        """
        Start a new consultation session.

        This method initiates a new consultation session based on the current
        consultation mode specified in the settings. If the consultation mode
        is set to DIALOGUE, it logs the start of a new session and initiates
        a chat session using the model.

        Returns:
            None
        """
        if self.settings.consultation_mode == ConsultationMode.DIALOGUE:
            self.logger.info("Starting new consultation session")
            self.chat_session = self.model.start_chat()

    def _get_ollama_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Kommuniziert mit Ollama, um eine Antwort zu erhalten.

        Args:
            messages (List[Dict[str, str]]): Liste der Nachrichten im Chat-Format.

        Returns:
            str: Die Antwort von Ollama.
        """
        try:
            response = ollama.chat(
                model=self.settings.active_model,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            self.logger.error(f"Fehler bei der Kommunikation mit Ollama: {e}")
            raise RuntimeError(f"Ollama-Fehler: {str(e)}")

async def _get_model_response_async(self, prompt: str) -> str:
        """
        Holt asynchron eine Antwort vom GenAI-Modell.
        
        Diese Methode implementiert eine robuste Fehlerbehandlung und 
        Wiederholungslogik für die Kommunikation mit dem GenAI-Modell. Sie
        berücksichtigt verschiedene Fehlerfälle wie Netzwerkprobleme oder
        Zeitüberschreitungen und versucht, diese angemessen zu behandeln.
        
        Args:
            prompt (str): Der zu verarbeitende Prompt
            
        Returns:
            str: Die generierte Antwort des Modells
            
        Raises:
            ModelConnectionError: Bei Verbindungsproblemen mit dem Modell
            ModelResponseError: Bei ungültigen oder fehlenden Antworten
            ConfigurationError: Bei Konfigurationsproblemen
        """
        # Überprüfe Modellkonfiguration
        if not self.model:
            raise ConfigurationError("GenAI-Modell nicht initialisiert")
            
        max_retries = 3
        retry_delay = 1.0  # Startverzögerung in Sekunden
        
        for attempt in range(max_retries):
            try:
                # Timeout für die gesamte Operation setzen
                async with asyncio.timeout(30):  # 30 Sekunden Timeout
                    if self.settings.consultation_mode == ConsultationMode.DIALOGUE:
                        if not self.chat_session:
                            self.chat_session = await self.model.start_chat_async()
                        response = await self.chat_session.send_message_async(prompt)
                    else:
                        response = await self.model.generate_content_async(prompt)
                    
                    # Validiere die Antwort
                    if not response or not hasattr(response, 'text'):
                        raise ModelResponseError(
                            model_name=self.settings.active_model,
                            response="Keine gültige Antwort erhalten"
                        )
                    
                    return response.text
                    
            except asyncio.TimeoutError:
                self.logger.warning(
                    f"Zeitüberschreitung bei Versuch {attempt + 1}/{max_retries}"
                )
                if attempt == max_retries - 1:
                    raise ModelConnectionError(
                        model_name=self.settings.active_model,
                        details="Wiederholte Zeitüberschreitungen"
                    )
                    
            except ConnectionError as e:
                self.logger.warning(
                    f"Verbindungsfehler bei Versuch {attempt + 1}/{max_retries}: {e}"
                )
                if attempt == max_retries - 1:
                    raise ModelConnectionError(
                        model_name=self.settings.active_model,
                        details=str(e)
                    )
                    
            # Exponentielles Backoff für Wiederholungsversuche
            await asyncio.sleep(retry_delay * (2 ** attempt))

    async def _get_ollama_response_async(self, prompt: str) -> str:
        """
        Holt asynchron eine Antwort vom Ollama-Modell.
        
        Diese Methode implementiert die asynchrone Kommunikation mit dem
        Ollama-API-Endpunkt. Sie nutzt aiohttp für asynchrone HTTP-Anfragen
        und implementiert eine robuste Fehlerbehandlung.
        
        Args:
            prompt (str): Der zu verarbeitende Prompt
            
        Returns:
            str: Die generierte Antwort des Modells
            
        Raises:
            ModelConnectionError: Bei Verbindungsproblemen mit Ollama
            ModelResponseError: Bei ungültigen oder fehlenden Antworten
            ConfigurationError: Bei Konfigurationsproblemen
        """
        if not self.settings.OLLAMA_HOST:
            raise ConfigurationError("Ollama-Host nicht konfiguriert")
            
        endpoint = f"{self.settings.OLLAMA_HOST}/api/generate"
        max_retries = 3
        retry_delay = 1.0
        
        # Bereite die Nachricht vor
        messages = [
            {'role': 'system', 'content': self.settings.system_prompt},
            {'role': 'user', 'content': prompt}
        ]
        
        async with aiohttp.ClientSession() as session:
            for attempt in range(max_retries):
                try:
                    async with asyncio.timeout(60):  # 60 Sekunden Timeout
                        async with session.post(
                            endpoint,
                            json={
                                'model': self.settings.active_model,
                                'messages': messages,
                                'stream': False  # Keine Stream-Verarbeitung
                            }
                        ) as response:
                            if response.status != 200:
                                error_text = await response.text()
                                raise ModelResponseError(
                                    model_name=self.settings.active_model,
                                    response=f"HTTP {response.status}: {error_text}"
                                )
                                
                            try:
                                data = await response.json()
                            except json.JSONDecodeError as e:
                                raise ModelResponseError(
                                    model_name=self.settings.active_model,
                                    response=f"Ungültige JSON-Antwort: {str(e)}"
                                )
                                
                            # Extrahiere und validiere die Antwort
                            if not data or 'response' not in data:
                                raise ModelResponseError(
                                    model_name=self.settings.active_model,
                                    response="Fehlender 'response' Schlüssel in Antwort"
                                )
                                
                            return data['response']
                            
                except asyncio.TimeoutError:
                    self.logger.warning(
                        f"Zeitüberschreitung bei Ollama-Anfrage "
                        f"(Versuch {attempt + 1}/{max_retries})"
                    )
                    if attempt == max_retries - 1:
                        raise ModelConnectionError(
                            model_name=self.settings.active_model,
                            details="Wiederholte Zeitüberschreitungen bei Ollama-Anfragen"
                        )
                        
                except aiohttp.ClientError as e:
                    self.logger.warning(
                        f"Netzwerkfehler bei Ollama-Anfrage "
                        f"(Versuch {attempt + 1}/{max_retries}): {e}"
                    )
                    if attempt == max_retries - 1:
                        raise ModelConnectionError(
                            model_name=self.settings.active_model,
                            details=f"Netzwerkfehler: {str(e)}"
                        )
                        
                # Exponentielles Backoff
                await asyncio.sleep(retry_delay * (2 ** attempt))
                
    async def _handle_chat_session_async(self) -> None:
        """
        Verwaltet die Chat-Session asynchron.
        
        Diese Methode kümmert sich um die Initialisierung und Verwaltung
        der Chat-Session im Dialogue-Modus. Sie stellt sicher, dass die
        Session korrekt initialisiert und bei Bedarf erneuert wird.
        
        Raises:
            ModelConnectionError: Bei Problemen mit der Session-Initialisierung
            ConfigurationError: Bei ungültiger Konfiguration
        """
        if self.settings.consultation_mode != ConsultationMode.DIALOGUE:
            return
            
        try:
            if self.settings.model_type == ModelType.GENAI:
                if not self.chat_session:
                    self.chat_session = await self.model.start_chat_async()
            else:
                # Ollama benötigt keine permanente Chat-Session
                pass
                
        except Exception as e:
            raise ModelConnectionError(
                model_name=self.settings.active_model,
                details=f"Chat-Session-Initialisierung fehlgeschlagen: {str(e)}"
            )
        
def ask_oracle(question: str, api_key: str = os.getenv("GENAI_API_KEY")) -> Dict[str, Any]:
    """
    Convenience function to get oracle response.

    Args:
        question (str): The question to ask the oracle.
        api_key (str, optional): The API key for authentication. Defaults to the value of the environment variable 'GENAI_API_KEY'.

    Returns:
        Dict[str, Any]: The response from the oracle.
    """
    oracle = YijingOracle(api_key=api_key)
    return oracle.get_response(question)

def formatiere_weissagung_markdown(weissagung: Dict[str, Any]) -> str:
    """
    Formatiert die Weissagung als Markdown-Text.
    Args:
        weissagung (Dict[str, Any]): Ein Wörterbuch, das die Weissagung enthält. 
            Es sollte die folgenden Schlüssel enthalten:
            - 'ursprung': Ein Wörterbuch mit Informationen über das ursprüngliche Hexagramm.
                - 'name': Der Name des Hexagramms.
                - 'nummer': Die Nummer des Hexagramms.
                - 'darstellung': Die symbolische Darstellung des Hexagramms.
                - 'trigrams': Ein Wörterbuch mit Informationen über die Trigramme.
                    - 'above': Ein Wörterbuch mit Informationen über das obere Trigramm.
                        - 'name': Der Name des oberen Trigramms.
                        - 'attributes': Die Attribute des oberen Trigramms.
                    - 'below': Ein Wörterbuch mit Informationen über das untere Trigramm.
                        - 'name': Der Name des unteren Trigramms.
                        - 'attributes': Die Attribute des unteren Trigramms.
                - 'bedeutung': Ein Wörterbuch mit der Grundbedeutung des Hexagramms.
                    - 'description': Die Beschreibung der Grundbedeutung.
                - 'urteil': Ein Wörterbuch mit dem Urteil des Hexagramms.
                    - 'description': Die Beschreibung des Urteils.
                    - 'analysis': Eine Liste von Analysepunkten des Urteils.
                - 'bild': Ein Wörterbuch mit dem Bild des Hexagramms.
                    - 'description': Die Beschreibung des Bildes.
                    - 'lesson': Die Lehre des Bildes.
            - 'wandelnde_linien': Ein Wörterbuch mit den wandelnden Linien.
                - 'deutungen': Eine Liste von Wörterbüchern mit den Deutungen der wandelnden Linien.
                    - 'position': Die Position der Linie.
                    - 'text': Der Text der Linie.
                    - 'interpretation': Die Deutung der Linie.
            - 'ergebnis': Ein Wörterbuch mit Informationen über das resultierende Hexagramm.
                - 'name': Der Name des Hexagramms.
                - 'nummer': Die Nummer des Hexagramms.
                - 'darstellung': Die symbolische Darstellung des Hexagramms.
                - 'trigrams': Ein Wörterbuch mit Informationen über die Trigramme.
                    - 'above': Ein Wörterbuch mit Informationen über das obere Trigramm.
                        - 'name': Der Name des oberen Trigramms.
                        - 'attributes': Die Attribute des oberen Trigramms.
                    - 'below': Ein Wörterbuch mit Informationen über das untere Trigramm.
                        - 'name': Der Name des unteren Trigramms.
                        - 'attributes': Die Attribute des unteren Trigramms.
                - 'bedeutung': Ein Wörterbuch mit der Grundbedeutung des Hexagramms.
                    - 'description': Die Beschreibung der Grundbedeutung.
                - 'urteil': Ein Wörterbuch mit dem Urteil des Hexagramms.
                    - 'description': Die Beschreibung des Urteils.
                    - 'analysis': Eine Liste von Analysepunkten des Urteils.
                - 'bild': Ein Wörterbuch mit dem Bild des Hexagramms.
                    - 'description': Die Beschreibung des Bildes.
                    - 'lesson': Die Lehre des Bildes.
    Returns:
        str: Die Weissagung formatiert als Markdown-Text.
    """
    ursprung = weissagung['ursprung']
    ergebnis = weissagung['ergebnis']
    
    md = [
        "# I GING WEISSAGUNG\n",
        
        "## URSPRÜNGLICHES HEXAGRAMM\n",
        f"### {ursprung['name']} (Nr. {ursprung['nummer']})\n",
        f"Symbol: {ursprung['darstellung']}\n",
        
        "#### Trigramme\n",
        f"Oben: {ursprung['trigrams']['above']['name']} ({ursprung['trigrams']['above']['attributes']})\n",
        f"Unten: {ursprung['trigrams']['below']['name']} ({ursprung['trigrams']['below']['attributes']})\n",
        
        "#### Grundbedeutung\n",
        f"{ursprung['bedeutung']['description']}\n",
        
        "#### Das Urteil\n",
        f"{ursprung['urteil']['description']}\n",
        
        "##### Analyse\n",
        "\n".join([f"- {punkt}" for punkt in ursprung['urteil']['analysis']]) + "\n",
        
        "#### Das Bild\n",
        f"{ursprung['bild']['description']}\n",
        f"**Lehre:** {ursprung['bild']['lesson']}\n",
        
        "## WANDELNDE LINIEN\n"
    ]
    
    for linie in weissagung['wandelnde_linien']['deutungen']:
        md.extend([
            f"### {linie['position']}. Linie\n",
            f"**Text:** {linie['text']}\n",
            f"**Deutung:** {linie['interpretation']}\n"
        ])
    
    md.extend([
        "## RESULTIERENDES HEXAGRAMM\n",
        f"### {ergebnis['name']} (Nr. {ergebnis['nummer']})\n",
        f"Symbol: {ergebnis['darstellung']}\n",
        
        "#### Trigramme\n",
        f"Oben: {ergebnis['trigrams']['above']['name']} ({ergebnis['trigrams']['above']['attributes']})\n",
        f"Unten: {ergebnis['trigrams']['below']['name']} ({ergebnis['trigrams']['below']['attributes']})\n",
        
        "#### Grundbedeutung\n",
        f"{ergebnis['bedeutung']['description']}\n",
        
        "#### Das Urteil\n",
        f"{ergebnis['urteil']['description']}\n",
        
        "##### Analyse\n",
        "\n".join([f"- {punkt}" for punkt in ergebnis['urteil']['analysis']]) + "\n",
        
        "#### Das Bild\n",
        f"{ergebnis['bild']['description']}\n",
        f"**Lehre:** {ergebnis['bild']['lesson']}\n"
    ])
    
    return "".join(md)

def analysiere_hexagramm_eigenschaften(weissagung: Dict[str, Any]) -> Dict[str, Any]:
    """Analysiert die Eigenschaften und Beziehungen der Hexagramme in einer Weissagung."""
    ursprung = weissagung['ursprung']
    ergebnis = weissagung['ergebnis']
    
    return {
        'trigramm_transformation': {
            'ursprung': {
                'oben': ursprung['trigrams']['above'],
                'unten': ursprung['trigrams']['below']
            },
            'ergebnis': {
                'oben': ergebnis['trigrams']['above'],
                'unten': ergebnis['trigrams']['below']
            }
        },
        'wandlungslinien_anzahl': len(weissagung['wandelnde_linien']['positionen']),
        'wandlungslinien_positionen': weissagung['wandelnde_linien']['positionen'],
        'kernaspekte': {
            'ursprung': {
                'name': ursprung['name'],
                'kernelement': ursprung['bedeutung']['description'].split('.')[0]
            },
            'ergebnis': {
                'name': ergebnis['name'],
                'kernelement': ergebnis['bedeutung']['description'].split('.')[0]
            }
        }
    }

# Funktion zum Formatieren der Analyse
def formatiere_analyse_markdown(analyse: Dict[str, Any]) -> str:
    """Formatiert die Hexagramm-Analyse als Markdown."""
    md = [
        "# ANALYSE DER HEXAGRAMM-TRANSFORMATION\n",
        
        "## Trigramm-Transformation\n",
        "### Ursprüngliches Hexagramm\n",
        f"- Oberes Trigramm: {analyse['trigramm_transformation']['ursprung']['oben']['name']} "
        f"({analyse['trigramm_transformation']['ursprung']['oben']['attributes']})\n",
        f"- Unteres Trigramm: {analyse['trigramm_transformation']['ursprung']['unten']['name']} "
        f"({analyse['trigramm_transformation']['ursprung']['unten']['attributes']})\n",
        
        "### Resultierendes Hexagramm\n",
        f"- Oberes Trigramm: {analyse['trigramm_transformation']['ergebnis']['oben']['name']} "
        f"({analyse['trigramm_transformation']['ergebnis']['oben']['attributes']})\n",
        f"- Unteres Trigramm: {analyse['trigramm_transformation']['ergebnis']['unten']['name']} "
        f"({analyse['trigramm_transformation']['ergebnis']['unten']['attributes']})\n",
        
        "## Wandlungslinien\n",
        f"- Anzahl der Wandlungen: {analyse['wandlungslinien_anzahl']}\n",
        f"- Positionen: {', '.join(map(str, analyse['wandlungslinien_positionen']))}\n",
        
        "## Kernaspekte\n",
        "### Ursprüngliches Hexagramm\n",
        f"- Name: {analyse['kernaspekte']['ursprung']['name']}\n",
        f"- Kernelement: {analyse['kernaspekte']['ursprung']['kernelement']}\n",
        
        "### Resultierendes Hexagramm\n",
        f"- Name: {analyse['kernaspekte']['ergebnis']['name']}\n",
        f"- Kernelement: {analyse['kernaspekte']['ergebnis']['kernelement']}\n"
    ]
    
    return "".join(md)

async def get_response_async(self, question: str) -> Dict[str, Any]:
        """
        Asynchrone Version der Weissagungs-Generierung.
        
        Diese Methode nutzt asynchrone Operationen, um die Antwortzeit zu verbessern,
        besonders bei der Interaktion mit den KI-Modellen. Sie implementiert die gleiche
        Fehlerbehandlung wie die synchrone Version, ist aber für asynchrone Ausführung
        optimiert.
        
        Args:
            question (str): Die Frage an das Orakel
            
        Returns:
            Dict[str, Any]: Ein Dictionary mit der Weissagung und zusätzlichen Informationen
            
        Raises:
            ModelConnectionError: Wenn keine Verbindung zum KI-Modell hergestellt werden kann
            ModelResponseError: Wenn die Antwort des Modells ungültig ist
            ResourceNotFoundError: Wenn erforderliche Ressourcen nicht gefunden werden
            HexagramTransformationError: Wenn bei der Hexagramm-Transformation ein Fehler auftritt
            ConfigurationError: Wenn die Konfiguration ungültig ist
        """
        try:
            self.logger.info(
                f"Starte asynchrone Verarbeitung im {self.settings.consultation_mode} "
                f"Modus mit Modell {self.settings.model_type.value}"
            )
            
            # Validiere die Konfiguration - kann synchron bleiben, da keine I/O-Operation
            self._validate_configuration()
            
            # Führe asynchrone Operationen parallel aus wo möglich
            try:
                # Erstelle Tasks für unabhängige Operationen
                hypergram_task = asyncio.create_task(self._cast_hypergram_async())
                
                # Warte auf das Ergebnis der Hexagramm-Generierung
                hypergram_data = await hypergram_task
                
            except ValueError as e:
                raise HexagramTransformationError(
                    error_detail=f"Async Hexagramm-Generierung fehlgeschlagen: {str(e)}"
                ) from e
            
            # Erstelle Hexagrammkontext - kann parallel zur Modellvorbereitung laufen
            try:
                context_task = asyncio.create_task(
                    self._create_hexagram_context_async(hypergram_data)
                )
                context = await context_task
                
            except FileNotFoundError as e:
                raise ResourceNotFoundError(
                    resource_path=str(e)
                ) from e
            
            # Generiere Prompt und hole Modellantwort
            try:
                # Erstelle den Prompt
                prompt = await self._generate_prompt_async(context, question)
                
                # Hole die Modellantwort basierend auf dem Modelltyp
                if self.settings.model_type == ModelType.GENAI:
                    response_text = await self._get_model_response_async(prompt)
                else:
                    response_text = await self._get_ollama_response_async(prompt)
                    
            except asyncio.TimeoutError as e:
                raise ModelConnectionError(
                    model_name=self.settings.active_model,
                    details="Zeitüberschreitung bei der Modellanfrage"
                ) from e
            except ConnectionError as e:
                raise ModelConnectionError(
                    model_name=self.settings.active_model,
                    details=str(e)
                ) from e
            except Exception as e:
                raise ModelResponseError(
                    model_name=self.settings.active_model,
                    response=str(e)
                ) from e
            
            # Erstelle und validiere die Antwort
            response = {
                'answer': response_text,
                'hypergram_data': hypergram_data.dict(),
                'hexagram_context': {
                    'original': context.original_hexagram['hexagram']['name'],
                    'resulting': context.resulting_hexagram['hexagram']['name'],
                    'changing_lines': context.changing_lines
                },
                'model_used': self.settings.active_model,
                'timestamp': datetime.now().isoformat(),
                'consultation_mode': self.settings.consultation_mode
            }
            
            # Validierung kann synchron bleiben
            self._validate_response(response)
            return response
            
        except Exception as e:
            self.logger.error(
                "Unerwarteter Fehler bei der asynchronen Generierung der Antwort",
                exc_info=True
            )
            raise

    async def _cast_hypergram_async(self):
        """
        Asynchrone Version der Hexagramm-Generierung.
        """
        # Da die Hexagramm-Generierung CPU-bound ist, nutzen wir einen ThreadPool
        return await asyncio.to_thread(cast_hypergram)

    async def _create_hexagram_context_async(self, hypergram_data):
        """
        Asynchrone Version der Kontext-Erstellung.
        """
        # Da dies hauptsächlich I/O-Operationen sind, können wir es asynchron machen
        original_number = hypergram_data.old_hexagram.to_binary_number() + 1
        resulting_number = hypergram_data.new_hexagram.to_binary_number() + 1
        
        # Lade Hexagramm-Daten parallel
        orig_data_task = asyncio.create_task(
            self._load_hexagram_data_async(original_number)
        )
        res_data_task = asyncio.create_task(
            self._load_hexagram_data_async(resulting_number)
        )
        
        # Warte auf beide Ergebnisse
        original_data, resulting_data = await asyncio.gather(
            orig_data_task, res_data_task
        )
        
        return HexagramContext(
            original_hexagram=original_data,
            changing_lines=[i + 1 for i in hypergram_data.changing_lines],
            resulting_hexagram=resulting_data
        )

    async def _generate_prompt_async(self, context, question: str) -> str:
        """
        Asynchrone Prompt-Generierung.
        """
        # Die Prompt-Generierung ist CPU-bound, daher nutzen wir einen ThreadPool
        return await asyncio.to_thread(
            self.hexagram_manager.get_consultation_prompt,
            context=context,
            question=question
        )

    async def _load_hexagram_data_async(self, number: int):
        """
        Asynchrone Version des Hexagramm-Daten-Ladens.
        """
        try:
            # Datei-I/O sollte asynchron sein
            resources_dir = self.resources_path / 'hexagram_json'
            hexagram_file = resources_dir / f'hexagram_{number:02d}.json'
            
            async with aiofiles.open(hexagram_file, mode='r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
                
        except FileNotFoundError as e:
            raise ResourceNotFoundError(
                resource_path=str(hexagram_file)
            ) from e
        except json.JSONDecodeError as e:
            raise ResourceValidationError(
                resource_path=str(hexagram_file),
                validation_errors=[f"Ungültiges JSON: {str(e)}"]
            )