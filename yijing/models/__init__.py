# yijing/models/__init__.py

"""
Oracle Module
============
Contains the main oracle class for generating I Ching readings and interpretations using GenAI.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import google.generativeai as genai
import logging
import os

from ..models import HypergramData, HexagramContext
from .generator import cast_hypergram
from .manager import HexagramManager
from ..enums import ConsultationMode
from ..config import Settings
from ..utils.resource_loader import load_system_prompt, load_yijing_text

logger = logging.getLogger(__name__)

@dataclass
class OracleSettings:
    """Settings for the Yijing Oracle."""
    system_prompt: Optional[str] = None
    yijing_text: Optional[str] = None
    active_model: str = "models/gemini-1.5-flash"
    consultation_mode: ConsultationMode = ConsultationMode.SINGLE

    def __post_init__(self):
        """Load appropriate system prompt and Yijing text if not provided."""
        if self.system_prompt is None:
            self.system_prompt = load_system_prompt(self.consultation_mode)
        
        if self.yijing_text is None:
            self.yijing_text = load_yijing_text()
        
        self.system_prompt = f"""{self.system_prompt}

Yijing Text Reference:
{self.yijing_text}
"""

class YijingOracle:
    """Oracle for generating I Ching readings and interpretations using GenAI."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        resources_path: Optional[Path] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ):
        """Initialize the YijingOracle with the given settings."""
        self.settings = Settings(**(custom_settings or {}))
        self.logger = self._setup_logging()
        
        # API key setup
        self.api_key = api_key or os.getenv("GENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not found. Please provide via parameter or "
                "environment variable 'GENAI_API_KEY'."
            )
        
        # Configure GenAI
        genai.configure(api_key=self.api_key)
        
        # Resources and manager setup
        self.resources_path = resources_path or Path(__file__).parent.parent / 'resources'
        self.hexagram_manager = HexagramManager(self.resources_path)
        
        try:
            self.model = genai.GenerativeModel(
                model_name=self.settings.model_name,
                system_instruction=self._get_system_prompt()
            )
            
            self.chat_session = None
            if self.settings.consultation_mode == ConsultationMode.DIALOGUE:
                self.chat_session = self.model.start_chat()
                
        except Exception as e:
            self.logger.error("Error during initialization", exc_info=True)
            raise RuntimeError(f"Oracle initialization error: {str(e)}")

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

    def _get_system_prompt(self) -> str:
        """Get the appropriate system prompt based on consultation mode."""
        try:
            prompt_path = self.resources_path / 'prompts' / 'system_prompt.txt'
            template_path = self.resources_path / 'prompts' / 'consultation_template.txt'
            
            if not prompt_path.exists() or not template_path.exists():
                raise FileNotFoundError("Required prompt files not found")
                
            with open(prompt_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
                
            with open(template_path, 'r', encoding='utf-8') as f:
                consultation_template = f.read()
                
            return f"{system_prompt}\n\nCONSULTATION TEMPLATE\n{'='*78}\n\n{consultation_template}"
            
        except Exception as e:
            self.logger.error(f"Error loading system prompt: {str(e)}")
            raise

    def get_response(self, question: str) -> Dict[str, Any]:
        """Generate an oracle response to the given question."""
        try:
            self.logger.info(f"Processing question in {self.settings.consultation_mode} mode")
            
            hypergram_data = cast_hypergram()
            context = self._create_hexagram_context(hypergram_data)
            prompt = self.hexagram_manager.get_consultation_prompt(
                context=context,
                question=question
            )
            
            if self.settings.consultation_mode == ConsultationMode.SINGLE:
                response = self._get_single_response(prompt)
            else:
                response = self._get_dialogue_response(prompt)
            
            return {
                'answer': response,
                'hypergram_data': hypergram_data.dict(),
                'hexagram_context': {
                    'original': context.original_hexagram['hexagram']['name'],
                    'resulting': context.resulting_hexagram['hexagram']['name'],
                    'changing_lines': context.changing_lines
                },
                'model_used': self.settings.model_name,
                'timestamp': datetime.now().isoformat(),
                'consultation_mode': self.settings.consultation_mode
            }
            
        except Exception as e:
            self.logger.error("Error generating response", exc_info=True)
            raise RuntimeError(f"Oracle error: {str(e)}")

    def _create_hexagram_context(self, hypergram_data: HypergramData) -> HexagramContext:
        """Create a hexagram context from hypergram data."""
        original_number = hypergram_data.old_hexagram.to_binary_number() + 1
        resulting_number = hypergram_data.new_hexagram.to_binary_number() + 1
        
        return self.hexagram_manager.create_reading_context(
            original_hex_num=original_number,
            changing_lines=hypergram_data.changing_lines,
            resulting_hex_num=resulting_number
        )

    def _get_single_response(self, prompt: str) -> str:
        """Generate a single response."""
        self.logger.debug("Generating single response")
        response = self.model.generate_content(prompt)
        
        if not response or not hasattr(response, 'text'):
            raise ValueError("No valid response received in single mode")
        
        return response.text

    def _get_dialogue_response(self, prompt: str) -> str:
        """Generate a response using the chat session."""
        self.logger.debug("Generating dialogue response")
        if not self.chat_session:
            self.chat_session = self.model.start_chat()
            
        response = self.chat_session.send_message(prompt)
        
        if not response or not hasattr(response, 'parts'):
            raise ValueError("No valid response received in dialogue mode")
            
        return response.parts[0].text

    def start_new_consultation(self):
        """Start a new consultation session."""
        if self.settings.consultation_mode == ConsultationMode.DIALOGUE:
            self.logger.info("Starting new consultation session")
            self.chat_session = self.model.start_chat()