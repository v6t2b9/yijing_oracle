# yijing/enums.py

from enum import Enum

class ConsultationMode(str, Enum):
    """
    ConsultationMode is an enumeration that defines the modes of interaction
    between the oracle and the model.

    Attributes:
        SINGLE (str): Represents a single interaction mode.
        DIALOGUE (str): Represents a dialogue interaction mode.
    """
    SINGLE = "single"
    DIALOGUE = "dialogue"

class LineType(str, Enum):
    """
    Represents the different types of lines in the Yijing system.

    Attributes:
        CHANGING_YIN (str): Represents a changing yin line (Value: 6).
        STABLE_YANG (str): Represents a stable yang line (Value: 7).
        STABLE_YIN (str): Represents a stable yin line (Value: 8).
        CHANGING_YANG (str): Represents a changing yang line (Value: 9).
    """
    CHANGING_YIN = "changing_yin"   # Value: 6
    STABLE_YANG = "stable_yang"     # Value: 7
    STABLE_YIN = "stable_yin"       # Value: 8
    CHANGING_YANG = "changing_yang" # Value: 9

class HexagramComponent(str, Enum):
    """
    HexagramComponent is an enumeration that identifies the different components of a hexagram reading.

    Attributes:
        ORIGINAL (str): Represents the original state of the hexagram.
        CHANGING (str): Represents the changing lines within the hexagram.
        RESULTING (str): Represents the resulting state of the hexagram after changes.
    """
    ORIGINAL = "original"
    CHANGING = "changing"
    RESULTING = "resulting"

class ResourceType(str, Enum):
    """
    An enumeration representing different types of resource files used by the system.

    Attributes:
        SYSTEM_PROMPT (str): Represents a system prompt resource file.
        YIJING_TEXT (str): Represents a Yijing text resource file.
        DIALOGUE_PROMPT (str): Represents a dialogue prompt resource file.
        SINGLE_PROMPT (str): Represents a single prompt resource file.
    """
    """Categorizes different types of resource files used by the system."""
    SYSTEM_PROMPT = "system_prompt"
    YIJING_TEXT = "yijing_text"
    DIALOGUE_PROMPT = "dialogue_prompt"
    SINGLE_PROMPT = "single_prompt"

class LogLevel(str, Enum):
    """
    LogLevel is an enumeration that defines various logging levels for system diagnostics.

    Attributes:
        DEBUG (str): Detailed information, typically of interest only when diagnosing problems.
        INFO (str): Confirmation that things are working as expected.
        WARNING (str): An indication that something unexpected happened, or indicative of some problem in the near future (e.g., ‘disk space low’). The software is still working as expected.
        ERROR (str): Due to a more serious problem, the software has not been able to perform some function.
        CRITICAL (str): A very serious error, indicating that the program itself may be unable to continue running.
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ModelType(str, Enum):
    """
    Defines the type of model to be used for generating responses.

    Attributes:
        GENAI (str): Use Google's Generative AI model
        OLLAMA (str): Use Ollama model
    """
    GENAI = "genai"
    OLLAMA = "ollama"

__all__ = [
    'ConsultationMode',
    'LineType',
    'HexagramComponent',
    'ResourceType',
    'LogLevel'
    'ModelType'
]