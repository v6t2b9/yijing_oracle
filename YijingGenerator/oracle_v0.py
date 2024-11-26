# oracle.py
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import json
import logging
from datetime import datetime
import os
import google.generativeai as genai
from .models import HypergramData
from .hypergram import cast_hypergram

@dataclass
class OracleSettings:
    """Settings for the Yijing Oracle"""
    active_model: str
    system_prompt: str
    debug: bool
    temperature: float
    max_tokens: int
    
    @classmethod
    def from_json(cls, path: Path) -> 'OracleSettings':
        """Load settings from a JSON file"""
        with open(path) as f:
            data = json.load(f)
        return cls(**data)

class YijingOracle:
    def __init__(
        self, 
        api_key: Optional[str] = None,
        settings_path: Optional[Path] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Yijing Oracle.
        
        Args:
            api_key: API key for the GenAI API
            settings_path: Path to JSON configuration file
            custom_settings: Custom settings as dict
        """
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
                model_name=self.settings.active_model,
                generation_config={
                    "temperature": self.settings.temperature,
                    "max_output_tokens": self.settings.max_tokens
                }
            )
        except Exception as e:
            self.logger.error("GenAI API configuration error", exc_info=True)
            raise RuntimeError(f"API configuration error: {e}")

    def _setup_logging(self) -> None:
        """Configure logging"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG if self.settings.debug else logging.INFO)

    def _load_settings(
        self, 
        settings_path: Optional[Path],
        custom_settings: Optional[Dict[str, Any]]
    ) -> OracleSettings:
        """Load oracle settings"""
        default_settings = {
            "active_model": "gemini-1.5-pro",
            "system_prompt": "You are a wise I Ching advisor...",
            "debug": True,
            "temperature": 0.9,
            "max_tokens": 1024
        }

        if settings_path and settings_path.exists():
            return OracleSettings.from_json(settings_path)
        elif custom_settings:
            return OracleSettings(**{**default_settings, **custom_settings})
        else:
            return OracleSettings(**default_settings)

    async def get_response(self, question: str) -> Dict[str, Any]:
        """
        Generate an oracle response for the given question.
        
        Returns:
            Dict with response and metadata:
            {
                'answer': str,  # The oracle's response
                'hypergram_data': Dict,  # The cast hexagrams
                'model_used': str,  # Model used
                'timestamp': str  # Generation timestamp
            }
        """
        try:
            self.logger.info(f"Processing question: {question}")
            
            # Cast hypergram
            hypergram_data = cast_hypergram()
            
            # Create chat context with system prompt
            chat = self.model.start_chat(context=self.settings.system_prompt)
            
            # Create prompt
            prompt = self._create_prompt(question, hypergram_data)
            
            # Generate response
            response = await chat.send_message_async(prompt)
            
            if not response or not response.text:
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
        """Create the prompt for the model"""
        return f"""Question: {question}

Hexagram Information:
- Old Hexagram: {hypergram_data.old_hexagram.to_unicode_representation()}
- New Hexagram: {hypergram_data.new_hexagram.to_unicode_representation()}
- Changing Lines: {', '.join(str(i+1) for i in hypergram_data.changing_lines)}

{self.settings.system_prompt}

Please interpret the hexagrams and answer the question."""