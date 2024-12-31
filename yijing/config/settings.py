# yijing/config/settings.py

"""
Settings Module
=============
Central configuration management for the I Ching oracle system.
"""

from pydantic import BaseModel, Field, field_validator, DirectoryPath
from typing import Optional, Any
from pathlib import Path
import os

from ..enums import ConsultationMode, LogLevel, ModelType

class Settings(BaseModel):
    """Global configuration settings for the I Ching oracle system."""
    
    # Core settings
    model_type: ModelType = ModelType.OLLAMA
    active_model: str = "llama2:latest"  # Default Ollama model
    consultation_mode: ConsultationMode = ConsultationMode.SINGLE
    
    # API Settings (nur für GenAI benötigt)
    api_key: Optional[str] = Field(
        default=None,
        env='GENAI_API_KEY',
        description='Google Generative AI API Key (only needed for GenAI)'
    )

    # Paths
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

    # Debug settings
    debug: bool = Field(
        default=False,
        env='DEBUG',
        description='Enable debug mode'
    )

    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        env='LOG_LEVEL',
        description='Logging level for the application'
    )
    
    log_file: Optional[Path] = Field(
        default=None,
        description='Path to log file'
    )

    model_config = {
        'protected_namespaces': ('settings_',),
        'env_file': '.env',
        'env_file_encoding': 'utf-8',
        'case_sensitive': False
    }

    def model_post_init(self, __context: Any) -> None:
        """Initialize derived settings after model creation."""
        if self.resources_dir is None:
            self.resources_dir = self.base_dir / 'resources'
                
        if self.prompt_templates_dir is None:
            self.prompt_templates_dir = self.resources_dir / 'prompts'
                
        if self.log_file is None and not self.debug:
            self.log_file = self.base_dir / 'logs' / 'yijing.log'

    @field_validator('api_key')
    def validate_api_key(cls, v: Optional[str]) -> Optional[str]:
        """Validate API key only if using GenAI."""
        if not v and cls.model_type == ModelType.GENAI:
            v = os.getenv('GENAI_API_KEY')
            if not v:
                raise ValueError(
                    "API Key ist erforderlich für GenAI. Bitte setzen Sie die "
                    "Umgebungsvariable GENAI_API_KEY oder übergeben "
                    "Sie den Key direkt."
                )
        return v

    def load_prompt_template(self, template_name: str) -> str:
        """Load a prompt template from the templates directory."""
        template_path = self.prompt_templates_dir / f"{template_name}.txt"
        if not template_path.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {template_path}"
            )
        return template_path.read_text(encoding='utf-8')

    def get_system_prompt(self) -> str:
        """Get the appropriate system prompt for the current consultation mode."""
        mode_template = self.load_prompt_template(
            f"{self.consultation_mode.value}_mode_prompt"
        )
        base_template = self.load_prompt_template("system_prompt")
        consultation_template = self.load_prompt_template("consultation_template")
        
        return f"{base_template}\n\n{mode_template}\n\n{consultation_template}"

# Create global settings instance
settings = Settings()