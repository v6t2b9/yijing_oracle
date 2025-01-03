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

from contextlib import AsyncExitStack
from asyncio import TimeoutError
import aiofiles

from ..models import HypergramData, HexagramContext, HypergramLine, Hypergram
from .generator import cast_hypergram
from .manager import HexagramManager
from ..enums import ConsultationMode
from ..config import Settings, settings, ModelType
from ..utils.resource_loader import load_system_prompt  # Nur load_system_prompt wird benötigt

import json
#from typing import Dict, Any, Optional

from datetime import datetime
from ..exceptions import (
    ModelConnectionError,
    ModelResponseError,
    ResourceNotFoundError,
    HexagramTransformationError,
    ConfigurationError
)

# Verzeichnisse initialisieren
project_dir = Path.cwd() # Aktuelles Arbeitsverzeichnis
resources_dir = project_dir / 'yijing' / 'resources' # Ressourcenverzeichnis


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
        api_key: Optional[str] = None,
        resources_path: Optional[Path] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ):
        # Initialize settings first
        self.settings = self._initialize_settings(custom_settings)
        self.logger = self._setup_logging()
        
        # API key setup for GenAI
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.settings.model_type == ModelType.GENAI and not self.api_key:
            raise ValueError(
                "API Schlüssel nicht gefunden. Bitte stellen Sie sicher, dass der API-Schlüssel bereitgestellt wird, "
                "entweder über einen Parameter oder die Umgebungsvariable 'GEMINI_API_KEY'."
            )
        
        # Configure GenAI if needed
        if self.settings.model_type == ModelType.GENAI:
            genai.configure(api_key=self.api_key)
        
        # Resources setup
        if resources_path:
            self.resources_path = resources_path
        else:
            # Get the path to the module's root directory
            module_root = Path(__file__).parent.parent
            self.resources_path = module_root / 'resources'
            self.prompts_path = self.resources_path / 'prompts'
        
        # Verify resources exist
        self._verify_resource_structure()
        
        # Initialize hexagram manager
        self.hexagram_manager = HexagramManager(self.resources_path)
        
        # Set up model based on settings
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
                # No specific initialization needed for Ollama
                pass
            else:
                raise ValueError(f"Unbekannter Modelltyp: {self.settings.model_type}")
                
        except Exception as e:
            self.logger.error("Fehler bei der Initialisierung", exc_info=True)
            raise RuntimeError(f"Oracle-Initialisierungsfehler: {str(e)}")

    def _initialize_settings(self, custom_settings: Optional[Dict[str, Any]] = None) -> Settings:
        """
        Initialize oracle settings by combining default settings with custom overrides.
        
        Args:
            custom_settings (Optional[Dict[str, Any]]): Custom settings to override defaults
            
        Returns:
            Settings: Initialized settings object
            
        Raises:
            ConfigurationError: If settings validation fails
        """
        try:
            # Start with default settings
            base_settings = Settings()
            
            if custom_settings:
                # Update with custom settings
                for key, value in custom_settings.items():
                    if hasattr(base_settings, key):
                        setattr(base_settings, key, value)
                    else:
                        self.logger.warning(f"Ignoring unknown setting: {key}")
            
            return base_settings
            
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize settings: {str(e)}")
        
        
    def _verify_resource_structure(self) -> None:
        """
        Verify that all required resource files exist in the prompts directory.
        
        This method checks for the existence of essential template files used by the oracle.
        The files should be located in the prompts subdirectory of the resources directory.
        
        Raises:
            FileNotFoundError: If any required template file is missing
        """
        required_files = [
            'consultation_template.txt',
            'system_prompt.txt'
        ]
        
        # Get the prompts directory path
        prompts_path = self.resources_path / 'prompts'
        
        # Check each required file
        for file in required_files:
            file_path = prompts_path / file
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Required template file not found: {file_path}\n"
                    f"Please ensure all template files are in the prompts directory."
                )
            
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

    def _get_system_prompt(self) -> str:
        """
        Load and combine the prompt templates for the oracle's system prompt.
        
        This method loads the base system prompt, consultation template, and 
        mode-specific template from the prompts directory and combines them 
        into a complete system prompt.
        
        Returns:
            str: The combined system prompt text
            
        Raises:
            FileNotFoundError: If any required template file is missing
        """
        try:
            # Get the prompts directory path
            prompts_path = self.resources_path / 'prompts'
            
            # Load each template from the prompts directory
            system_template = (prompts_path / 'system_prompt.txt').read_text(encoding='utf-8')
            consultation_template = (prompts_path / 'consultation_template.txt').read_text(encoding='utf-8')
            mode_template = (prompts_path / f"{self.settings.consultation_mode.value}_mode_prompt.txt").read_text(encoding='utf-8')
            
            # Combine the templates
            return f"{system_template}\n\n{mode_template}\n\n{consultation_template}"
                    
        except Exception as e:
            self.logger.error(f"Error loading prompt templates: {str(e)}")
            raise
        
    def _setup_logging(self) -> logging.Logger:
        """Set up basic logging."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
            logger.setLevel(
                logging.DEBUG if self.settings.debug else logging.INFO
            )
        return logger

    def get_response(self, question: str) -> Dict[str, Any]:
        """
        Generiert eine Weissagung basierend auf der Frage und dem gewählten Modell.
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
            
            # Generiere Prompt
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

    def _get_ollama_response(self, prompt: str) -> str:
        """
        Kommuniziert mit Ollama, um eine Antwort zu erhalten.

        Args:
            prompt (str): Der zu verarbeitende Prompt

        Returns:
            str: Die Antwort von Ollama
        """
        try:
            # Formatiere die Nachrichten im korrekten Format für Ollama
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            response = ollama.chat(
                model=self.settings.active_model,
                messages=messages
            )
            
            if not isinstance(response, dict) or 'message' not in response:
                raise ModelResponseError(
                    model_name=self.settings.active_model,
                    response="Ungültiges Antwortformat von Ollama"
                )
                
            return response['message']['content']
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Kommunikation mit Ollama: {e}")
            raise ModelResponseError(
                model_name=self.settings.active_model,
                response=str(e)
            )
   
    def _get_ollama_response(self, prompt: str) -> str:
        """Kommuniziert mit Ollama."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            response = ollama.chat(
                model=self.settings.active_model,
                messages=messages
            )
            
            return response['message']['content']
                
        except Exception as e:
            self.logger.error(f"Fehler bei der Kommunikation mit Ollama: {e}")
            raise ModelResponseError(
                model_name=self.settings.active_model,
                response=str(e)
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