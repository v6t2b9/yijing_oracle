"""
Resource Loader Module
====================
Utilities for loading and managing I Ching resources.

This module provides functions for:
- Loading text resources (prompts, templates)
- Loading and parsing hexagram data
- Managing resource paths and files
"""

from pathlib import Path
from typing import Dict, Optional
import json
import logging
from ..enums import ConsultationMode

logger = logging.getLogger(__name__)

def load_yijing_text() -> str:
    """Load the complete I Ching text content.
    
    Returns:
        str: Complete I Ching text content
        
    Raises:
        FileNotFoundError: If the text file cannot be found
    """
    resources_dir = Path(__file__).parent.parent / 'resources'
    yijing_file = resources_dir / 'yijing.txt'
    
    if not yijing_file.exists():
        raise FileNotFoundError(
            f"Yijing text file not found at {yijing_file}"
        )
        
    return yijing_file.read_text(encoding='utf-8')

def load_system_prompt(mode: ConsultationMode) -> str:
    """Load system prompt based on consultation mode.
    
    Args:
        mode (ConsultationMode): SINGLE or DIALOGUE mode
        
    Returns:
        str: System prompt content for the specified mode
        
    Raises:
        FileNotFoundError: If prompt file cannot be found
    """
    resources_dir = Path(__file__).parent.parent / 'resources'
    prompt_file = resources_dir / f'{mode.value}_system_prompt.txt'
    
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"System prompt file not found at {prompt_file}"
        )
        
    return prompt_file.read_text(encoding='utf-8')

def load_hexagram_data(number: int) -> Dict:
    """Load data for a specific hexagram.
    
    Args:
        number (int): Hexagram number (1-64)
        
    Returns:
        Dict: Complete hexagram data
        
    Raises:
        FileNotFoundError: If hexagram file cannot be found
    """
    resources_dir = Path(__file__).parent.parent / 'resources/hexagram_json'
    hexagram_file = resources_dir / f'hexagram_{number:02d}.json'
    
    if not hexagram_file.exists():
        raise FileNotFoundError(
            f"Hexagram file not found: {hexagram_file}"
        )
        
    with open(hexagram_file, 'r', encoding='utf-8') as f:
        return json.load(f)
    

# yijing/utils/resource_loader.py

# Füge diese Methoden zur vorhandenen Klasse hinzu:

def validate_resources(self) -> bool:
    """Validate all resource files before loading.
    
    Returns:
        bool: True if all validations pass
    """
    from .validate_resources import validate_all_resources
    return validate_all_resources()

def ensure_resource_structure(self) -> None:
    """Ensure all required resource directories exist."""
    # Erstelle Verzeichnisse falls sie nicht existieren
    directories = [
        self.resources_dir,
        self.resources_dir / 'hexagram_json',
        self.resources_dir / 'trigram_json',
        self.resources_dir / 'text',
        self.resources_dir / 'text' / 'interpretations',
        self.resources_dir / 'schemas'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")