# __init__.py
from .models import (
    Hypergram,
    HypergramData, 
    HypergramLine,
    Hexagram,
    HexagramLine
)

from .hypergram import cast_hypergram

from .utils import load_yijing_text

from .enums import ConsultationMode
from .oracle import YijingOracle, OracleSettings, ask_oracle

__version__ = "0.0.1"
__author__ = "JayKay"
__author_email__ = "xxx"

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
    "load_yijing_text",
    "ConsultationMode"
]