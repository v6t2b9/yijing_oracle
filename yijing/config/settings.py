# yijing/config/settings.py

"""
Settings Module
=============
Central configuration management for the I Ching oracle system.
"""

from pydantic import BaseModel, Field, field_validator, DirectoryPath
from typing import Optional, Dict, Any
from pathlib import Path
import os

from ..enums import ConsultationMode, LogLevel
from ..enums import ModelType  # Importiere ModelType aus enums statt lokaler Definition

from ..constants import DEFAULT_MODEL

from enum import Enum
from dataclasses import dataclass

"""
class ModelType(Enum):
    GENAI = "genai"
    OLLAMA = "ollama"
"""

class Settings(BaseModel):
    """Global configuration settings for the I Ching oracle system."""

    model_type: ModelType = ModelType.OLLAMA # ModelType.GEMINI
    
    active_model: str = "models/gemini-1.5-flash"
    consultation_mode: ConsultationMode = ConsultationMode.SINGLE
    system_prompt: Optional[str] = None
    yijing_text: Optional[str] = None

    model_config = {
        'protected_namespaces': ('settings_',),
        'env_file': '.env',
        'env_file_encoding': 'utf-8',
        'case_sensitive': False
    }

    # API Settings
    api_key: str = Field(
        default=None,
        env='GENAI_API_KEY',
        description='Google Generative AI API Key'
    )

    # Model Settings
    model_name: str = Field(
        default=DEFAULT_MODEL,
        description='Name of the AI model to use'
    )

    # Path Settings
    base_dir: DirectoryPath = Field(
        default=Path(__file__).parent.parent,
        description='Base directory of the package'
    )
    
    resources_dir: DirectoryPath = Field(
        default=None,
        description='Directory containing resource files'
    )
    
    prompt_templates_dir: DirectoryPath = Field(
        default=None,
        description='Directory containing prompt templates'
    )

    # Oracle Settings
    consultation_mode: ConsultationMode = Field(
        default=ConsultationMode.SINGLE,
        description='Consultation mode (single/dialogue)'
    )
    
    default_language: str = Field(
        default="de",
        description='Default language for responses'
    )

    # Logging Settings
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        env='LOG_LEVEL',
        description='Logging level for the application'
    )
    
    log_file: Optional[Path] = Field(
        default=None,
        description='Path to log file'
    )

    # Debug Settings
    debug: bool = Field(
        default=False,
        env='DEBUG',
        description='Enable debug mode'
    )

    # Ollama Settings
    ollama_host: str = Field(
        default="http://localhost:11434",
        env='OLLAMA_HOST',
        description='Ollama API host address'
    )
    
    def model_post_init(self, __context: Any) -> None:
        """Initialize derived settings after model creation."""
        # Set default paths relative to base_dir if not explicitly set
        if self.resources_dir is None:
            self.resources_dir = self.base_dir / 'resources'
            
        if self.prompt_templates_dir is None:
            self.prompt_templates_dir = self.base_dir / 'config' / 'prompts'
            
        if self.log_file is None and not self.debug:
            self.log_file = self.base_dir / 'logs' / 'yijing.log'

    @field_validator('api_key')
    def validate_api_key(cls, v: Optional[str]) -> str:
        """Validate that an API key is provided."""
        if not v:
            v = os.getenv('GENAI_API_KEY')
            if not v:
                raise ValueError(
                    "API Key ist erforderlich. Bitte setzen Sie die "
                    "Umgebungsvariable GENAI_API_KEY oder übergeben "
                    "Sie den Key direkt."
                )
        return v

    def load_prompt_template(self, template_name: str) -> str:
        """Load a prompt template from the templates directory.
        
        Args:
            template_name (str): Name of the template file
            
        Returns:
            str: Content of the template file
            
        Raises:
            FileNotFoundError: If template file cannot be found
        """
        template_path = self.prompt_templates_dir / f"{template_name}.txt"
        if not template_path.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {template_path}"
            )
        return template_path.read_text(encoding='utf-8')

    def get_system_prompt(self) -> str:
        """Get the appropriate system prompt for the current consultation mode.
        
        Returns:
            str: Complete system prompt
        """
        mode_template = self.load_prompt_template(
            f"{self.consultation_mode.value}_mode_prompt"
        )
        base_template = self.load_prompt_template("system_prompt")
        consultation_template = self.load_prompt_template("consultation_template")
        
        return f"{base_template}\n\n{mode_template}\n\n{consultation_template}"

# Create global settings instance
settings = Settings()