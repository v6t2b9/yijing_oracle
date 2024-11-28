# projektordner/yijing/oracle.py

from datetime import datetime
import google.generativeai as genai
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import json
import logging
import os
from .models import HypergramData
from .hypergram import cast_hypergram
from enum import Enum, auto

class ConsultationMode(str, Enum):
    """Defines how the oracle interacts with the model"""
    SINGLE = "single"     # Uses generate_content for independent readings
    DIALOGUE = "dialogue" # Uses chat for continuous conversation

@dataclass
class OracleSettings:
    """Settings for the Yijing Oracle"""
    system_prompt: str = "Du bist ein einfühlsames und weises I-Ging-Orakel..."
    yijing_text: Optional[str] = None
    active_model: str = "models/gemini-1.5-flash"
    consultation_mode: ConsultationMode = ConsultationMode.SINGLE

    def __post_init__(self):
        """Load Yijing text if not provided and combine with system prompt"""
        if self.yijing_text is None:
            self.yijing_text = load_yijing_text()
        
        # Combine system prompt with Yijing text
        self.system_prompt = f"""{self.system_prompt}

Yijing Text Referenz:
{self.yijing_text}
"""
        
    @classmethod
    def from_json(cls, path: Path) -> 'OracleSettings':
        """Load settings from JSON file"""
        with open(path) as f:
            data = json.load(f)
        return cls(**data)

# projektordner/yijing/oracle.py

class YijingOracle:
    def __init__(
        self, 
        api_key: Optional[str] = None,
        settings_path: Optional[Path] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ):
        """Initialize Yijing Oracle with support for both single and dialogue modes"""
        self.settings = self._load_settings(settings_path, custom_settings)
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # API Key Setup
        self.api_key = api_key or os.getenv("GENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not found. Please provide via parameter or "
                "environment variable 'GENAI_API_KEY'."
            )

        # GenAI Setup
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=self.settings.active_model,
                system_instruction=self.settings.system_prompt
            )
            # Initialize chat session if in dialogue mode
            self.chat_session = None
            if self.settings.consultation_mode == ConsultationMode.DIALOGUE:
                self.chat_session = self.model.start_chat()
        except Exception as e:
            self.logger.error("GenAI API configuration error", exc_info=True)
            raise RuntimeError(f"API configuration error: {e}")

    def get_response(self, question: str) -> Dict[str, Any]:
        """Generate oracle response using either single or dialogue mode"""
        try:
            self.logger.info(f"Processing question in {self.settings.consultation_mode} mode")
            
            hypergram_data = cast_hypergram()
            prompt = self._create_prompt(question, hypergram_data)
            
            if self.settings.consultation_mode == ConsultationMode.SINGLE:
                response = self._get_single_response(prompt)
            else:
                response = self._get_dialogue_response(prompt)
            
            return {
                'answer': response,
                'hypergram_data': hypergram_data.dict(),
                'model_used': self.settings.active_model,
                'timestamp': datetime.now().isoformat(),
                'consultation_mode': self.settings.consultation_mode
            }
            
        except Exception as e:
            self.logger.error("Error generating response", exc_info=True)
            raise RuntimeError(f"Oracle error: {str(e)}")

    def _get_single_response(self, prompt: str) -> str:
        """Generate a single response using generate_content"""
        self.logger.debug("Generating single response")
        response = self.model.generate_content(prompt)
        
        if not response or not hasattr(response, 'text'):
            raise ValueError("No valid response received in single mode")
        
        return response.text

    def _get_dialogue_response(self, prompt: str) -> str:
        """Generate a response using the chat session"""
        self.logger.debug("Generating dialogue response")
        if not self.chat_session:
            self.logger.debug("Creating new chat session")
            self.chat_session = self.model.start_chat()
            
        response = self.chat_session.send_message(prompt)
        
        if not response or not hasattr(response, 'parts') or len(response.parts) == 0:
            raise ValueError("No valid response received in dialogue mode")
            
        return response.parts[0].text

    def start_new_consultation(self):
        """Start a new consultation session in dialogue mode"""
        if self.settings.consultation_mode == ConsultationMode.DIALOGUE:
            self.logger.info("Starting new consultation session")
            self.chat_session = self.model.start_chat()
    '''
    def __init__(
        self, 
        api_key: Optional[str] = None,
        settings_path: Optional[Path] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ):
        """Initialize Yijing Oracle"""
        # First load settings as they're needed by other initialization steps
        self.settings = self._load_settings(settings_path, custom_settings)
        
        # Then set up logging with the loaded settings
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # API Key Setup
        self.api_key = api_key or os.getenv("GENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not found. Please provide via parameter or "
                "environment variable 'GENAI_API_KEY'."
            )

        # GenAI Setup
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name="models/gemini-1.5-flash",  # Aktualisiert auf das neueste Modell
                system_instruction=self.settings.system_prompt
            )
        except Exception as e:
            self.logger.error("GenAI API configuration error", exc_info=True)
            raise RuntimeError(f"API configuration error: {e}")
    '''
    def _setup_logging(self) -> None:
        """Configure logging"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _load_settings(
        self, 
        settings_path: Optional[Path],
        custom_settings: Optional[Dict[str, Any]]
    ) -> OracleSettings:
        """Load oracle settings"""
        default_settings = {
            "active_model": "gemini-1.5-pro",
            "system_prompt": "Yijing Oracle Advisor",
        }

        if settings_path and settings_path.exists():
            return OracleSettings.from_json(settings_path)
        elif custom_settings:
            return OracleSettings(**{**default_settings, **custom_settings})
        else:
            return OracleSettings(**default_settings)

    def get_response(self, question: str) -> Dict[str, Any]:
        """Generate oracle response for given question"""
        try:
            self.logger.info(f"Processing question: {question}")
            
            hypergram_data = cast_hypergram()
            
            # Create the prompt and generate response
            prompt = self._create_prompt(question, hypergram_data)
            response = self.model.generate_content(prompt)
            
            if not response or not hasattr(response, 'text'):
                raise ValueError("No valid response received")
                
            return {
                'answer': response.text,
                'hypergram_data': hypergram_data.dict(),
                'model_used': self.settings.active_model,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error("Error generating response", exc_info=True)
            raise RuntimeError(f"Oracle error: {str(e)}")

    def _create_prompt(self, question: str, hypergram_data: HypergramData) -> str:
        """Create model prompt"""
        return f"""Question: {question}

Hexagram Information:
- Old Hexagram: {hypergram_data.old_hexagram.to_unicode_representation()}
- New Hexagram: {hypergram_data.new_hexagram.to_unicode_representation()}
- Changing Lines: {', '.join(str(i+1) for i in hypergram_data.changing_lines)}

Please interpret the hexagrams and answer the question."""

# Helper function for easy usage
def ask_oracle(question: str, api_key: str = os.getenv("GENAI_API_KEY")) -> Dict[str, Any]:
    """Convenience function to get oracle response"""
    oracle = YijingOracle(api_key=api_key)
    return oracle.get_response(question)
