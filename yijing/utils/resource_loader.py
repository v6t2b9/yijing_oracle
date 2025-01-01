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

def load_system_prompt(mode: ConsultationMode) -> str:
    """Load system prompt based on consultation mode.
    
    Args:
        mode (ConsultationMode): Consultation mode

    Returns:
        str: System prompt text

    Raises:
        FileNotFoundError: If prompt file cannot be found.
    """
    resources_dir = Path(__file__).parent.parent / 'resources/prompts'
    prompt_file = resources_dir / f'{mode.value}_mode_prompt.txt'
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"System prompt file not found: {prompt_file}")
        
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