# yijing/constants.py

from typing import Dict, Literal, Final

# Line values
CHANGING_YIN: Final[int] = 6
STABLE_YANG: Final[int] = 7
STABLE_YIN: Final[int] = 8
CHANGING_YANG: Final[int] = 9

# Valid line values
VALID_LINE_VALUES: Final[tuple] = (CHANGING_YIN, STABLE_YANG, STABLE_YIN, CHANGING_YANG)

# Hexagram constraints
MAX_BINARY_VALUE: Final[int] = 63  # 111111 in binary
HEXAGRAM_LINE_COUNT: Final[int] = 6

# Model defaults
DEFAULT_MODEL: Final[str] = "models/gemini-1.5-flash"

# Line transformations
LINE_TYPE_MAPPING: Final[Dict[int, str]] = {
    CHANGING_YIN: "changing_yin",
    STABLE_YANG: "stable_yang",
    STABLE_YIN: "stable_yin",
    CHANGING_YANG: "changing_yang"
}

TRANSFORMATION_VALUES: Final[Dict[str, Literal[0, 1]]] = {
    "changing_yin": 1,   # Changes to Yang
    "changing_yang": 0   # Changes to Yin
}

# Unicode representations
YIN_SYMBOL: Final[str] = "⚋"
YANG_SYMBOL: Final[str] = "⚊"