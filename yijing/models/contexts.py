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

@dataclass
class HexagramContext:
    """Represents the complete context for a hexagram reading."""
    original_hexagram: Dict[str, Any]
    changing_lines: List[int]
    resulting_hexagram: Dict[str, Any]
    
    def get_relevant_line_interpretations(self) -> List[Dict[str, str]]:
        return [
            {
                'position': self.original_hexagram['lines'][i-1]['position'],
                'text': self.original_hexagram['lines'][i-1]['text'],
                'interpretation': self.original_hexagram['lines'][i-1]['interpretation']
            }
            for i in self.changing_lines
            if 0 <= i-1 < len(self.original_hexagram['lines'])
        ]

class HypergramData(BaseModel):
    """Contains the complete data for a hypergram reading including transformations."""
    hypergram: Hypergram
    old_hexagram: Hexagram
    new_hexagram: Hexagram
    changing_lines: List[int]