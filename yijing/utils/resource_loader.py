# yijing/utils/resource_loader.py

"""
Resource Loader Module
====================
Utilities for loading and managing I Ching resources.

This module provides functions for loading various types of resources:
- Text resources (prompts, templates, Yijing texts)
- Hexagram data
- System configuration files
"""

from pathlib import Path
from typing import Dict, Optional
import json
import logging
from ..enums import ConsultationMode

logger = logging.getLogger(__name__)

def load_system_prompt(mode: ConsultationMode) -> str:
    """
    Load system prompt based on consultation mode.
    
    Args:
        mode (ConsultationMode): The consultation mode to load the prompt for

    Returns:
        str: The system prompt text for the specified mode

    Raises:
        FileNotFoundError: If the prompt file cannot be found
    """
    resources_dir = Path(__file__).parent.parent / 'resources/prompts'
    prompt_file = resources_dir / f'{mode.value}_mode_prompt.txt'
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"System prompt file not found: {prompt_file}")
        
    return prompt_file.read_text(encoding='utf-8')

def load_hexagram_data(number: int) -> Dict:
    """
    Load data for a specific hexagram.
    
    Args:
        number (int): Hexagram number (1-64)
        
    Returns:
        Dict: Complete hexagram data
        
    Raises:
        FileNotFoundError: If the hexagram file cannot be found
    """
    resources_dir = Path(__file__).parent.parent / 'resources/hexagram_json'
    hexagram_file = resources_dir / f'hexagram_{number:02d}.json'
    
    if not hexagram_file.exists():
        raise FileNotFoundError(f"Hexagram file not found: {hexagram_file}")
        
    with open(hexagram_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_yijing_text(resource_name: str) -> str:
    """
    Load specific Yijing text resources.
    
    This function loads text resources like consultation templates,
    interpretation guides, or other static text content used by the oracle.
    
    Args:
        resource_name (str): Name of the text resource to load
        
    Returns:
        str: Content of the requested text resource
        
    Raises:
        FileNotFoundError: If the requested resource cannot be found
    """
    resources_dir = Path(__file__).parent.parent / 'resources'
    resource_file = resources_dir / f'{resource_name}.txt'
    
    if not resource_file.exists():
        raise FileNotFoundError(f"Resource file not found: {resource_file}")
        
    return resource_file.read_text(encoding='utf-8')