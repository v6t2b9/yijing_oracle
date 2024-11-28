# yijing/enums.py

from enum import Enum

class ConsultationMode(str, Enum):
    """Defines how the oracle interacts with the model."""
    SINGLE = "single"
    DIALOGUE = "dialogue"

class LineType(str, Enum):
    """Represents the different types of lines in the Yijing system."""
    CHANGING_YIN = "changing_yin"   # Value: 6
    STABLE_YANG = "stable_yang"     # Value: 7
    STABLE_YIN = "stable_yin"       # Value: 8
    CHANGING_YANG = "changing_yang" # Value: 9

class HexagramComponent(str, Enum):
    """Identifies the different components of a hexagram reading."""
    ORIGINAL = "original"
    CHANGING = "changing"
    RESULTING = "resulting"

class ResourceType(str, Enum):
    """Categorizes different types of resource files used by the system."""
    SYSTEM_PROMPT = "system_prompt"
    YIJING_TEXT = "yijing_text"
    DIALOGUE_PROMPT = "dialogue_prompt"
    SINGLE_PROMPT = "single_prompt"

class LogLevel(str, Enum):
    """Defines logging levels for system diagnostics."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

__all__ = [
    'ConsultationMode',
    'LineType',
    'HexagramComponent',
    'ResourceType',
    'LogLevel'
]