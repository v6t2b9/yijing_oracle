# yijing/settings.py

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional
from pathlib import Path
from .enums import ConsultationMode

class Settings(BaseSettings):
    """Zentrale Konfiguration für das Yijing Oracle System.
    
    Diese Klasse nutzt Pydantic für:
    - Automatische Umgebungsvariablen-Validierung
    - Typsicherheit
    - Automatisches Environment-Loading
    """
    
    # Erforderliche Einstellungen
    api_key: str = Field(
        default=None,
        env='GENAI_API_KEY',
        description='Google Generative AI API Key'
    )
    
    # Optionale Einstellungen mit sinnvollen Defaults
    model_name: str = Field(
        default="models/gemini-1.5-flash",
        description='Name des zu verwendenden KI-Modells'
    )
    consultation_mode: ConsultationMode = Field(
        default=ConsultationMode.SINGLE,
        description='Beratungsmodus (single/dialogue)'
    )
    debug: bool = Field(
        default=False,
        description='Debug-Modus aktivieren'
    )

    # Ressourcen-Management
    resources_dir: Path = Field(
        default=Path(__file__).parent / 'resources',
        description='Verzeichnis für Ressourcendateien'
    )

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False

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