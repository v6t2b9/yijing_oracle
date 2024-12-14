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

class HypergramData(BaseModel):
    """Complete oracle reading data containing both hypergram and hexagram information."""
    hypergram: Hypergram
    old_hexagram: Hexagram
    new_hexagram: Hexagram
    changing_lines: List[int]


@dataclass
class HexagramContext:
    """Represents the complete context for a hexagram reading."""
    original_hexagram: Dict[str, Any]
    changing_lines: List[int]
    resulting_hexagram: Dict[str, Any]
    
    def get_relevant_line_interpretations(self) -> List[Dict[str, str]]:
        """Retrieves interpretations for the changing lines."""
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


@dataclass
class ConsultationPrompt:
    """Structures the consultation prompt according to the I Ching oracle format."""
    question: str
    original_hexagram: Dict[str, Any]
    changing_lines: List[Dict[str, str]]
    resulting_hexagram: Dict[str, Any]

    def format_changing_lines(self) -> str:
        """Formats changing lines with their interpretations."""
        return "\n".join([
            f"Position {line['position']}:\n"
            f"Bedeutung: {line['text']}\n"
            f"Interpretation: {line['interpretation']}\n"
            for line in self.changing_lines
        ])

    def generate(self) -> str:
        """Generates the complete consultation prompt."""
        return f"""
1. AUSGANGSSITUATION
==============================================================================
{self.original_hexagram['hexagram']['name']}

Grundlegende Symbolik:
{self.original_hexagram['hexagram']['meaning']['description']}

Das Urteil:
{self.original_hexagram['judgment']['description']}

Das Bild:
{self.original_hexagram['image']['description']}

2. WANDLUNGSPROZESS
==============================================================================
Wandelnde Linien und ihre Bedeutung:
{self.format_changing_lines()}

3. ZUKUNFTSTENDENZ
==============================================================================
{self.resulting_hexagram['hexagram']['name']}

Sich entfaltende Möglichkeit:
{self.resulting_hexagram['hexagram']['meaning']['description']}

Das Urteil der sich entwickelnden Situation:
{self.resulting_hexagram['judgment']['description']}

Das Bild der Zukunftstendenz:
{self.resulting_hexagram['image']['description']}

BERATUNGSANFRAGE
==============================================================================
Frage: {self.question}
"""