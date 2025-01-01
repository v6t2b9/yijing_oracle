# yijing/models/lines.py

"""
Lines Module
===========
Contains the basic line classes for the I Ching system: HypergramLine and HexagramLine.
These represent the fundamental building blocks of hexagrams.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional
import logging
from ..enums import LineType
from ..constants import (
    LINE_TYPE_MAPPING,
    YIN_SYMBOL,
    YANG_SYMBOL
)

logger = logging.getLogger(__name__)

class HypergramLine(BaseModel):
    """A single line in a hypergram that can change state."""
    value: Literal[6, 7, 8, 9]
    
    def is_yin(self) -> bool:
        return self.value in (6, 8)  # Vereinfachte Logik
        
    def is_yang(self) -> bool:
        return self.value in (7, 9)  # Vereinfachte Logik
        
    def is_changing(self) -> bool:
        return self.value in (6, 9)  # Vereinfachte Logik
        
    def transforms_to(self) -> Literal[0, 1]:
        return 1 if self.value == 6 else 0 if self.value == 9 else None
    
class HexagramLine(BaseModel):
    """A single fixed line in a hexagram."""
    value: Literal[0, 1] = Field(
        ...,
        description="Value of the hexagram line (0: Yin, 1: Yang)"
    )

    def to_unicode_symbol(self) -> str:
        """Get the Unicode symbol representation of the line."""
        return YANG_SYMBOL if self.value == 1 else YIN_SYMBOL