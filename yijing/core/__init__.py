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

from .oracle import YijingOracle
from .manager import HexagramManager
from .generator import cast_hypergram

__all__ = [
    'YijingOracle',
    'HexagramManager',
    'cast_hypergram'
]