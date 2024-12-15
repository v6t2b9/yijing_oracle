# yijing/core/loader.py

"""
Loader Module
=============
Contains functions for loading hexagram data from JSON files.
"""
from pathlib import Path
import json
from typing import Dict

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