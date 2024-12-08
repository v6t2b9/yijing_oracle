# yijing/settings.py

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, DirectoryPath
from typing import Optional
from pathlib import Path
from .enums import ConsultationMode, LogLevel
from .constants import DEFAULT_MODEL

class Settings(BaseSettings):
    """Zentrale Konfiguration für das Yijing Oracle System."""

    model_config = {
        'protected_namespaces': ('settings_',), # Schützt Einstellungen vor Überschreibung
        'env_file': '.env', # Standardmäßig .env-Datei verwenden
        'env_file_encoding': 'utf-8', # Standardmäßig UTF-8 verwenden
        'case_sensitive': False # Groß-/Kleinschreibung ignorieren
    }

    # API Configuration
    api_key: str = Field( # API-Key für Google Generative AI
        default=None, # Standardmäßig nicht gesetzt
        env='GENAI_API_KEY', # Umgebungsvariable
        description='Google Generative AI API Key' # Beschreibung
    )

    # Model Configuration
    model_name: str = Field(
        default=DEFAULT_MODEL,
        description='Name of the AI model to use'
    )

    # Logging Configuration
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        env='LOG_LEVEL',
        description='Logging level for the application'
    )

    # Consultation Configuration
    consultation_mode: ConsultationMode = Field(
        default=ConsultationMode.SINGLE,
        description='Consultation mode (single/dialogue)'
    )

    # Resource Configuration
    resources_dir: DirectoryPath = Field(
        default=Path(__file__).parent / 'resources',
        description='Directory containing resource files'
    )

    # Debug Configuration
    debug: bool = Field(
        default=False,
        env='DEBUG',
        description='Enable debug mode'
    )

    def get_system_prompt(self) -> str:
        """Lädt den System-Prompt basierend auf dem Beratungsmodus."""
        prompt_file = self.resources_dir / f'{self.consultation_mode}_system_prompt.txt'
        if not prompt_file.exists():
            raise FileNotFoundError(
                f"System prompt file nicht gefunden: {prompt_file}"
            )
        return prompt_file.read_text(encoding='utf-8')

    def get_yijing_text(self) -> str:
        """Lädt den Yijing-Basistext."""
        yijing_file = self.resources_dir / 'yijing.txt'
        if not yijing_file.exists():
            raise FileNotFoundError(
                f"Yijing text file nicht gefunden: {yijing_file}"
            )
        return yijing_file.read_text(encoding='utf-8')

    @field_validator('api_key')
    def validate_api_key(cls, v: Optional[str]) -> str:
        """Stellt sicher, dass ein API-Key vorhanden ist."""
        if not v:
            raise ValueError(
                "API Key ist erforderlich. Bitte setzen Sie die "
                "Umgebungsvariable GENAI_API_KEY oder übergeben "
                "Sie den Key direkt."
            )
        return v

# Singleton-Instanz der Konfiguration
settings = Settings()

__all__ = ['settings', 'Settings']