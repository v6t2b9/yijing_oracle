# yijing/core/__init__.py

"""
Core Package
===========
Contains the core functionality of the I Ching oracle system.

This package provides:
- Oracle implementation (YijingOracle)
- Hexagram management (HexagramManager)
- Reading generation (cast_hypergram)
"""

from .oracle import YijingOracle, ask_oracle
from .generator import cast_hypergram
from .manager import HexagramManager

__all__ = [
    'YijingOracle',
    'ask_oracle',
    'cast_hypergram',
    'HexagramManager'
]