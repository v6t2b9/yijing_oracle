# yijing/models/contexts.py

"""
Contexts Module
==============
Contains context classes that handle the interpretation and consultation aspects
of I Ching readings.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from pydantic import BaseModel
from .hexagrams import Hexagram, Hypergram

class HexagramContext:
    """Represents the complete context for a hexagram reading."""
    original_hexagram: Dict[str, Any]
    changing_lines: List[int]
    resulting_hexagram: Dict[str, Any]
    
    def get_relevant_line_interpretations(self) -> List[Dict[str, str]]:
        relevant_lines = []
        for line_num in self.changing_lines:
            array_index = line_num - 1
            if 0 <= array_index < len(self.original_hexagram['lines']):
                line_data = self.original_hexagram['lines'][array_index]
                relevant_lines.append({
                    'position': line_data['position'],
                    'text': line_data['text'],
                    'interpretation': line_data['interpretation']
                })
        return relevant_lines