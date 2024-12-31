# yijing/core/generator.py

"""
Generator Module
==============
Contains functions for generating I Ching readings through random line generation.
"""

import random
import logging
from ..models import (
    Hypergram,
    HypergramData, 
    HypergramLine
)

logger = logging.getLogger(__name__)

def cast_hypergram() -> HypergramData:
    """
    Generate a complete I Ching reading through random line generation.
    
    This function creates a Hypergram by generating six random lines, where each line
    can have one of four values:
        6: Changing yin
        7: Stable yang
        8: Stable yin
        9: Changing yang
    
    Returns:
        HypergramData: A complete reading containing:
            - The original hypergram
            - The old (initial) hexagram
            - The new (transformed) hexagram
            - List of changing line indices
    
    Example:
        >>> data = cast_hypergram()
        >>> print(f"Old hexagram: {data.old_hexagram.to_unicode_representation()}")
        >>> print(f"Changes at lines: {data.changing_lines}")
        >>> print(f"New hexagram: {data.new_hexagram.to_unicode_representation()}")
    """
    logger.debug("Generating six random lines for hypergram")
    
    # Generate six random lines
    lines = [
        HypergramLine(value=random.choice([6, 7, 8, 9])) 
        for _ in range(6)
    ]
    
    hypergram = Hypergram(lines=lines)
    
    return HypergramData(
        hypergram=hypergram,
        old_hexagram=hypergram.old_hexagram(),
        new_hexagram=hypergram.new_hexagram(),
        changing_lines=hypergram.changing_lines()
    )