# projektordner/config.py
#import os
#from typing import Dict, Literal, Optional
from pydantic_settings import BaseSettings
from pydantic import Field#, validator

class ProjectSettings(BaseSettings):
    """Basis-Projektkonfiguration"""
    api_key: str = Field(..., env='API_KEY')  # ... macht
    debug: bool = Field(default=False, env='DEBUG')
    
    class Config:
        env_file = '.env'
        extra = 'ignore'


# Konfiguration des API-Schlüssels
#API_KEY = os.environ.get("API_KEY")
#if not API_KEY:
#    raise ValueError("API_KEY Umgebungsvariable ist nicht gesetzt.")