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
    
    @property
    def line_type(self) -> LineType:
        """Get the line type from the numerical value."""
        return LineType(LINE_TYPE_MAPPING[self.value])

    def is_yin(self) -> bool:
        """Check if the line is yin (either stable or changing)."""
        logger.debug(f"Checking if line {self.value} is yin")
        return self.line_type in [LineType.CHANGING_YIN, LineType.STABLE_YIN]

    def is_yang(self) -> bool:
        """Check if the line is yang (either stable or changing)."""
        logger.debug(f"Checking if line {self.value} is yang")
        return self.line_type in [LineType.CHANGING_YANG, LineType.STABLE_YANG]

    def is_changing(self) -> bool:
        """Check if the line is changing (either yin or yang)."""
        logger.debug(f"Checking if line {self.value} is changing")
        return self.line_type in [LineType.CHANGING_YIN, LineType.CHANGING_YANG]

    def transforms_to(self) -> Optional[Literal[0, 1]]:
        """Get the transformation value for changing lines."""
        logger.debug(f"Determining transformation for line {self.value}")
        transforms = {
            LineType.CHANGING_YIN: 1,  # Changes to Yang
            LineType.CHANGING_YANG: 0  # Changes to Yin
        }
        return transforms.get(self.line_type)

    def to_unicode_symbol(self) -> str:
        """Get the Unicode symbol representation of the line."""
        return YANG_SYMBOL if self.is_yang() else YIN_SYMBOL


class HexagramLine(BaseModel):
    """A single fixed line in a hexagram."""
    value: Literal[0, 1] = Field(
        ...,
        description="Value of the hexagram line (0: Yin, 1: Yang)"
    )

    def to_unicode_symbol(self) -> str:
        """Get the Unicode symbol representation of the line."""
        return YANG_SYMBOL if self.value == 1 else YIN_SYMBOL