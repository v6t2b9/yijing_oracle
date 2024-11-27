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
        """Load settings from JSON file"""
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
                self.settings.active_model,
                system_instruction=self.settings.system_prompt
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
            "system_prompt": "Yijing Oracle Advisor",
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

    def get_response(self, question: str) -> Dict[str, Any]:
        """Generate oracle response for given question"""
        try:
            self.logger.info(f"Processing question: {question}")
            
            hypergram_data = cast_hypergram()
            
            # Create the prompt and start chat
            prompt = self._create_prompt(question, hypergram_data)
            chat = self.model.start_chat()
            response = chat.send_message(
                prompt,
                #temperature=self.settings.temperature,
                #max_output_tokens=self.settings.max_tokens
            )
            
            if not response or not hasattr(response, 'parts') or len(response.parts) == 0:
                raise ValueError("No valid response received")
                
            return {
                'answer': response.parts[0].text,
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
