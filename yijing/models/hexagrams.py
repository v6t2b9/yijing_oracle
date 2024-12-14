# yijing/models/hexagrams.py
 
"""
Hexagrams Module
===============
Contains the Hexagram and Hypergram classes that represent complete I Ching figures.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict
import logging
from .lines import HexagramLine, HypergramLine
from ..constants import HEXAGRAM_LINE_COUNT

logger = logging.getLogger(__name__)

class Hexagram(BaseModel):
    """A collection of six fixed lines representing a hexagram."""
    
    lines: List[HexagramLine] = Field(
        ...,
        description="List of exactly six lines forming the hexagram"
    )

    @field_validator('lines')
    def validate_lines(cls, v: List[HexagramLine]) -> List[HexagramLine]:
        """Validate that the hexagram has exactly six lines."""
        logger.debug("Validating hexagram lines")
        if len(v) != HEXAGRAM_LINE_COUNT:
            raise ValueError("A hexagram must contain exactly 6 lines")
        return v

    def yin_yang_count(self) -> Dict[str, int]:
        """Count the number of yin and yang lines in the hexagram."""
        logger.debug("Counting yin and yang lines")
        return {
            'yin': sum(1 for line in self.lines if line.value == 0),
            'yang': sum(1 for line in self.lines if line.value == 1)
        }

    def to_binary_number(self) -> int:
        """Convert the hexagram to its binary number representation (0-63)."""
        return int(''.join(str(line.value) for line in self.lines), 2)

    def to_unicode_representation(self) -> str:
        """Get the Unicode string representation of the hexagram."""
        return ''.join(line.to_unicode_symbol() for line in self.lines)


class Hypergram(BaseModel):
    """A collection of six potentially changing lines."""
    
    lines: List[HypergramLine] = Field(
        ...,
        description="List of exactly six lines forming the hypergram"
    )

    @field_validator('lines')
    def validate_lines(cls, v: List[HypergramLine]) -> List[HypergramLine]:
        """Validate that the hypergram has exactly six lines."""
        logger.debug("Validating hypergram lines")
        if len(v) != HEXAGRAM_LINE_COUNT:
            raise ValueError("A hypergram must contain exactly 6 lines")
        return v

    def old_hexagram(self) -> Hexagram:
        """Get the initial hexagram before any transformations."""
        logger.debug("Creating old hexagram")
        return Hexagram(lines=[
            HexagramLine(value=0 if line.is_yin() else 1)
            for line in self.lines
        ])

    def new_hexagram(self) -> Hexagram:
        """Get the resulting hexagram after all transformations."""
        logger.debug("Creating new hexagram")
        return Hexagram(lines=[
            HexagramLine(value=line.transforms_to() if line.is_changing() 
                        else (0 if line.is_yin() else 1))
            for line in self.lines
        ])

    def changing_lines(self) -> List[int]:
        """Get the indices of changing lines in the hypergram."""
        logger.debug("Finding changing lines")
        return [i for i, line in enumerate(self.lines) if line.is_changing()]