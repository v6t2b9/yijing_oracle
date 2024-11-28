# yijing/enums.py

from enum import Enum

class ConsultationMode(str, Enum):
    """Defines how the oracle interacts with the model"""
    SINGLE = "single"     # Uses generate_content for independent readings
    DIALOGUE = "dialogue" # Uses chat for continuous conversation