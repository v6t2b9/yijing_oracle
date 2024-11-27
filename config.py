# projektordner/config.py

from pydantic_settings import BaseSettings
from pydantic import Field#, validator

class ProjectSettings(BaseSettings):
    """Basis-Projektkonfiguration"""
    api_key: str = Field(..., env='API_KEY')  # ... macht
    debug: bool = Field(default=False, env='DEBUG')
    
    class Config:
        env_file = '.env'
        extra = 'ignore'