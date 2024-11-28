# __init__.py
from .models import (
    Hypergram,
    HypergramData, 
    HypergramLine,
    Hexagram,
    HexagramLine
)

from .hypergram import cast_hypergram
from .oracle import YijingOracle, OracleSettings, ask_oracle  # Hauptklassen aus oracle.py

from .utils import load_yijing_text

__version__ = "0.1.0"
__author__ = "Your Name"
__author_email__ = "your.email@example.com"

__all__ = [
    "Hypergram",
    "HypergramData",
    "HypergramLine", 
    "Hexagram",
    "HexagramLine",
    "cast_hypergram",
    "YijingOracle",
    "OracleSettings",
    "ask_oracle",
    "load_yijing_text"
]