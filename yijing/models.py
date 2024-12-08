"""
Yijing Oracle Generator Models
=============================

This module provides Pydantic models for generating and manipulating Yijing (I Ching) divination results.
It includes models for lines, hexagrams, and the complete oracle reading process.

Main Components:
---------------
- LineType: Enum for different types of lines
- HypergramLine: Represents a single line with changing properties
- HexagramLine: Represents a fixed line in a hexagram
- Hexagram: Collection of six fixed lines
- Hypergram: Collection of six potentially changing lines
- HypergramData: Complete oracle reading data

Example:
--------
>>> from yijing_models import Hypergram, HypergramLine
>>> hypergram = Hypergram(lines=[
...     HypergramLine(value=6),  # Changing Yin
...     HypergramLine(value=7),  # Stable Yang
...     HypergramLine(value=8),  # Stable Yin
...     HypergramLine(value=9),  # Changing Yang
...     HypergramLine(value=7),  # Stable Yang
...     HypergramLine(value=8)   # Stable Yin
... ])
>>> old_hex = hypergram.old_hexagram()
>>> new_hex = hypergram.new_hexagram()
"""
import logging
from dataclasses import dataclass
from pydantic import BaseModel, Field, field_validator, computed_field
from typing import List, Literal, Optional, Dict, Any  # Added Any to the typing imports
from .enums import LineType
from .constants import (
    LINE_TYPE_MAPPING,
    TRANSFORMATION_VALUES,
    YIN_SYMBOL,
    YANG_SYMBOL,
    HEXAGRAM_LINE_COUNT,
    MAX_BINARY_VALUE
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class HypergramLine(BaseModel):
    """
    A single line in a hypergram, representing one of the six positions.

    This class represents a line that can be either stable or changing,
    and either yin or yang. The line's properties are determined by its
    numerical value.

    Attributes:
        value (Literal[6, 7, 8, 9]): The numerical value determining the line's type:
            - 6: Changing yin
            - 7: Stable yang
            - 8: Stable yin
            - 9: Changing yang

    Properties:
        line_type (LineType): The type of the line, computed from its value

    Methods:
        is_yin(): Check if the line is yin (stable or changing)
        is_yang(): Check if the line is yang (stable or changing)
        is_changing(): Check if the line is changing (yin or yang)
        transforms_to(): Get the transformation value for changing lines
        to_unicode_symbol(): Get the Unicode representation of the line

    Example:
        >>> line = HypergramLine(value=6)
        >>> line.is_yin()
        True
        >>> line.is_changing()
        True
        >>> line.transforms_to()
        1
    """
    value: Literal[6, 7, 8, 9]
    
    @computed_field
    def line_type(self) -> LineType:
        """Get the line type from the numerical value."""
        return LineType(LINE_TYPE_MAPPING[self.value])

    def is_yin(self) -> bool:
        """
        Check if the line is yin (either stable or changing).

        Returns:
            bool: True if the line is yin (value 6 or 8)

        Example:
            >>> line = HypergramLine(value=6)
            >>> line.is_yin()
            True
        """
        logger.debug(f"Checking if line {self.value} is yin")
        return self.line_type in [LineType.CHANGING_YIN, LineType.STABLE_YIN]

    def is_yang(self) -> bool:
        """
        Check if the line is yang (either stable or changing).

        Returns:
            bool: True if the line is yang (value 7 or 9)

        Example:
            >>> line = HypergramLine(value=7)
            >>> line.is_yang()
            True
        """
        logger.debug(f"Checking if line {self.value} is yang")
        return self.line_type in [LineType.CHANGING_YANG, LineType.STABLE_YANG]

    def is_changing(self) -> bool:
        """
        Check if the line is changing (either yin or yang).

        Returns:
            bool: True if the line is changing (value 6 or 9)

        Example:
            >>> line = HypergramLine(value=6)
            >>> line.is_changing()
            True
        """
        logger.debug(f"Checking if line {self.value} is changing")
        return self.line_type in [LineType.CHANGING_YIN, LineType.CHANGING_YANG]

    def transforms_to(self) -> Optional[Literal[0, 1]]:
        """
        Get the transformation value for a changing line.

        Returns:
            Optional[Literal[0, 1]]: 
                - 1 if changing from yin to yang (value 6)
                - 0 if changing from yang to yin (value 9)
                - None if the line is not changing

        Example:
            >>> line = HypergramLine(value=6)
            >>> line.transforms_to()
            1
        """
        logger.debug(f"Determining transformation for line {self.value}")
        transforms = {
            LineType.CHANGING_YIN: 1,  # Changes to Yang
            LineType.CHANGING_YANG: 0  # Changes to Yin
        }
        return transforms.get(self.line_type)

    def to_unicode_symbol(self) -> str:
        """
        Get the Unicode symbol representation of the line.

        Returns:
            str: Unicode symbol representing the line:
                - '䷀' for yang lines
                - '䷁' for yin lines

        Example:
            >>> line = HypergramLine(value=7)
            >>> line.to_unicode_symbol()
            '䷀'
        """
        return "䷀" if self.is_yang() else "䷁"

class HexagramLine(BaseModel):
    """
    A single fixed line in a hexagram.

    Attributes:
        value (Literal[0, 1]): The value of the line:
            - 0: Yin line
            - 1: Yang line

    Methods:
        to_unicode_symbol(): Get the Unicode representation of the line

    Example:
        >>> line = HexagramLine(value=1)
        >>> line.to_unicode_symbol()
        '䷀'
    """
    value: Literal[0, 1] = Field(
        ...,
        description="Value of the hexagram line (0: Yin, 1: Yang)"
    )

    def to_unicode_symbol(self) -> str:
        """
        Get the Unicode symbol representation of the line.

        Returns:
            str: Unicode symbol representing the line:
                - '䷀' for yang lines (value 1)
                - '䷁' for yin lines (value 0)

        Example:
            >>> line = HexagramLine(value=1)
            >>> line.to_unicode_symbol()
            '䷀'
        """
        return "䷀" if self.value == 1 else "䷁"

class Hexagram(BaseModel):
    """
    A collection of six fixed lines representing a hexagram.

    A hexagram is a figure composed of six stacked horizontal lines,
    where each line can be either yin (broken) or yang (solid).

    Attributes:
        lines (List[HexagramLine]): List of exactly six lines

    Methods:
        yin_yang_count(): Count the number of yin and yang lines
        to_binary_number(): Convert the hexagram to its numerical representation
        to_unicode_representation(): Get the Unicode symbol representation

    Raises:
        ValueError: If the number of lines is not exactly six

    Example:
        >>> hex = Hexagram(lines=[HexagramLine(value=0) for _ in range(6)])
        >>> hex.yin_yang_count()
        {'yin': 6, 'yang': 0}
    """
    lines: List[HexagramLine] = Field(
        ...,
        description="List of exactly six lines forming the hexagram"
    )

    @field_validator('lines', mode='before')
    def validate_lines(cls, v: List) -> List[HexagramLine]:
        """
        Validate that the hexagram has exactly six lines.

        Args:
            v (List): List of lines to validate

        Returns:
            List[HexagramLine]: The validated list of lines

        Raises:
            ValueError: If the list does not contain exactly 6 lines

        Example:
            >>> Hexagram(lines=[HexagramLine(value=0) for _ in range(5)])
            ValueError: A hexagram must contain exactly 6 lines
        """
        logger.debug("Validating hexagram lines")
        if len(v) != 6:
            raise ValueError("A hexagram must contain exactly 6 lines")
        return v

    def yin_yang_count(self) -> Dict[str, int]:
        """
        Count the number of yin and yang lines in the hexagram.

        Returns:
            Dict[str, int]: Dictionary containing counts:
                - 'yin': Number of yin lines (value 0)
                - 'yang': Number of yang lines (value 1)

        Example:
            >>> hex = Hexagram(lines=[HexagramLine(value=0) for _ in range(6)])
            >>> hex.yin_yang_count()
            {'yin': 6, 'yang': 0}
        """
        logger.debug("Counting yin and yang lines")
        return {
            'yin': sum(1 for line in self.lines if line.value == 0),
            'yang': sum(1 for line in self.lines if line.value == 1)
        }

    def to_binary_number(self) -> int:
        """
        Convert the hexagram to its binary number representation (0-63).

        Returns:
            int: The decimal number corresponding to the binary representation

        Example:
            >>> hex = Hexagram(lines=[HexagramLine(value=1) for _ in range(6)])
            >>> hex.to_binary_number()
            63
        """
        return int(''.join(str(line.value) for line in self.lines), 2)

    def to_unicode_representation(self) -> str:
        """
        Get the Unicode string representation of the hexagram.

        Returns:
            str: String of Unicode symbols representing the hexagram lines

        Example:
            >>> hex = Hexagram(lines=[HexagramLine(value=1) for _ in range(6)])
            >>> hex.to_unicode_representation()
            '䷀䷀䷀䷀䷀䷀'
        """
        return ''.join(line.to_unicode_symbol() for line in self.lines)

class Hypergram(BaseModel):
    """
    A collection of six potentially changing lines representing a hypergram.

    A hypergram represents the initial state of a Yijing reading, where
    lines can be either stable or changing. It can be transformed into
    two hexagrams: the initial (old) hexagram and the resulting (new) hexagram.

    Attributes:
        lines (List[HypergramLine]): List of exactly six lines

    Methods:
        old_hexagram(): Get the initial hexagram
        new_hexagram(): Get the resulting hexagram
        changing_lines(): Get the indices of changing lines
        to_unicode_representation(): Get the Unicode representation

    Raises:
        ValueError: If the number of lines is not exactly six

    Example:
        >>> hypergram = Hypergram(lines=[HypergramLine(value=6) for _ in range(6)])
        >>> old_hex = hypergram.old_hexagram()
        >>> new_hex = hypergram.new_hexagram()
    """
    lines: List[HypergramLine] = Field(
        ...,
        description="List of exactly six lines forming the hypergram"
    )

    @field_validator('lines')
    def validate_lines(cls, v: List[HypergramLine]) -> List[HypergramLine]:
        """
        Validate that the hypergram has exactly six lines.

        Args:
            v (List[HypergramLine]): List of lines to validate

        Returns:
            List[HypergramLine]: The validated list of lines

        Raises:
            ValueError: If the list does not contain exactly 6 lines
        """
        logger.debug("Validating hypergram lines")
        if len(v) != 6:
            raise ValueError("A hypergram must contain exactly 6 lines")
        return v

    def old_hexagram(self) -> Hexagram:
        """
        Get the initial hexagram before any transformations.

        Returns:
            Hexagram: The initial hexagram based on the current yin/yang state

        Example:
            >>> hypergram = Hypergram(lines=[HypergramLine(value=6) for _ in range(6)])
            >>> hex = hypergram.old_hexagram()
            >>> hex.yin_yang_count()
            {'yin': 6, 'yang': 0}
        """
        logger.debug("Creating old hexagram")
        return Hexagram(lines=[
            HexagramLine(value=0 if line.is_yin() else 1)
            for line in self.lines
        ])

    def new_hexagram(self) -> Hexagram:
        """
        Get the resulting hexagram after all transformations.

        Returns:
            Hexagram: The new hexagram after applying all line changes

        Example:
            >>> hypergram = Hypergram(lines=[HypergramLine(value=6) for _ in range(6)])
            >>> hex = hypergram.new_hexagram()
            >>> hex.yin_yang_count()
            {'yin': 0, 'yang': 6}
        """
        logger.debug("Creating new hexagram")
        return Hexagram(lines=[
            HexagramLine(value=line.transforms_to() if line.is_changing() else (0 if line.is_yin() else 1))
            for line in self.lines
        ])

    def changing_lines(self) -> List[int]:
        """
        Get the indices of changing lines in the hypergram.

        Returns:
            List[int]: List of indices (0-5) of changing lines

        Example:
            >>> hypergram = Hypergram(lines=[HypergramLine(value=6) for _ in range(6)])
            >>> hypergram.changing_lines()
            [0, 1, 2, 3, 4, 5]
        """
        logger.debug("Finding changing lines")
        return [i for i, line in enumerate(self.lines) if line.is_changing()]
    
class HypergramData(BaseModel):
    """
    Complete oracle reading data containing both hypergram and hexagram information.

    Attributes:
        hypergram (Hypergram): The initial hypergram state
        old_hexagram (Hexagram): The initial hexagram before transformations
        new_hexagram (Hexagram): The resulting hexagram after transformations
        changing_lines (List[int]): Indices of changing lines in the hypergram

    Example:
        >>> hypergram = Hypergram(lines=[HypergramLine(value=6) for _ in range(6)])
        >>> data = HypergramData(hypergram=hypergram)
    """
    hypergram: Hypergram
    old_hexagram: Hexagram = Field(
        ...,
        description="Initial hexagram before transformations"
    )
    new_hexagram: Hexagram = Field(
        ...,
        description="Resulting hexagram after transformations"
    )
    changing_lines: List[int] = Field(
        ...,
        description="Indices of changing lines in the hypergram"
    )

# yijing/models.py - Ergänze die bestehende Datei um diese Klasse

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

Als weises I Ging Orakel werde ich nun eine tiefgründige Interpretation und Beratung 
anbieten, die folgende Aspekte berücksichtigt:

1. Die gegenwärtige Situation im Licht des Ausgangshexagramms
2. Den Wandlungsprozess durch die sich verändernden Linien
3. Die Zukunftstendenz im resultierenden Hexagramm
4. Praktische Reflexions- und Handlungsempfehlungen
5. Konkrete Übungen zur Integration der Erkenntnisse

Die Antwort wird in würdevoller und zugleich verständlicher Sprache formuliert,
die traditionelle Weisheit des I Ging mit modernem Verständnis verbindet.
"""
    
    # yijing/models.py

# Add this to your existing imports at the top
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class HexagramContext:
    """Represents the complete context for a hexagram reading.
    
    This class encapsulates all the information needed for interpreting
    a hexagram reading, including the original hexagram, changing lines,
    and the resulting hexagram.
    
    Attributes:
        original_hexagram: Dictionary containing the initial hexagram data
        changing_lines: List of line numbers that are changing
        resulting_hexagram: Dictionary containing the final hexagram data
    """
    original_hexagram: Dict[str, Any]
    changing_lines: List[int]
    resulting_hexagram: Dict[str, Any]
    
    def get_relevant_line_interpretations(self) -> List[Dict[str, str]]:
        """Retrieves interpretations for the changing lines.
        
        Returns:
            A list of dictionaries containing position, text, and interpretation
            for each changing line.
        """
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