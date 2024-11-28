# yijing/__init__.py

from .settings import settings
from .models import (
    Hypergram,
    HypergramData, 
    HypergramLine,
    Hexagram,
    HexagramLine
)
from .oracle import YijingOracle
from .enums import ConsultationMode

__version__ = "0.0.1"
__author__ = "JayKay"

__all__ = [
    "settings",
    "YijingOracle",
    "Hypergram",
    "HypergramData",
    "HypergramLine", 
    "Hexagram",
    "HexagramLine",
    "ConsultationMode"
]