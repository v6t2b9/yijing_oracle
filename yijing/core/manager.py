# yijing/core/manager.py

from pathlib import Path
from typing import Dict, Any, List
import logging

from ..models import HexagramContext
from .loader import load_hexagram_data

logger = logging.getLogger(__name__)

class HexagramManager:
    """
    HexagramManager manages hexagram data and contexts for Yijing oracle readings.
    
    This class provides centralized management of hexagram data and reading contexts,
    handling file operations and data validation for the oracle system.
    
    Attributes:
        resources_path (Path): Path to the resources directory containing hexagram data.
        
    Methods:
        get_hexagram_data(number: int) -> Dict[str, Any]:
            Retrieves the data for a specific hexagram number.
            
        create_reading_context(original_hex_num: int, changing_lines: List[int], 
                             resulting_hex_num: int) -> HexagramContext:
            Creates a complete reading context based on hexagram numbers and changing lines.
            
        get_consultation_prompt(context: HexagramContext, question: str) -> str:
            Generates a consultation prompt based on the context and question.
    """
    def __init__(self, resources_path: Path):
        """
        Initialize the HexagramManager.
        
        Args:
            resources_path (Path): Path to the resources directory.
        """
        self.resources_path = resources_path
        logger.debug(f"Initialized HexagramManager with resources path: {resources_path}")

    def get_hexagram_data(self, number: int) -> Dict[str, Any]:
        """
        Retrieve data for a specific hexagram.
        
        Args:
            number (int): The hexagram number (must be between 1 and 64).
            
        Returns:
            Dict[str, Any]: The complete data associated with the hexagram.
            
        Raises:
            ValueError: If the hexagram number is not between 1 and 64.
        """
        if not 1 <= number <= 64:
            raise ValueError(f"Invalid hexagram number: {number}")
            
        return load_hexagram_data(number)

    def create_reading_context(
        self,
        original_hex_num: int,
        changing_lines: List[int],
        resulting_hex_num: int
    ) -> HexagramContext:
        """
        Create a complete reading context.
        
        Args:
            original_hex_num (int): The number of the original hexagram.
            changing_lines (List[int]): The lines that are changing in the reading.
            resulting_hex_num (int): The number of the resulting hexagram.
            
        Returns:
            HexagramContext: A complete context for the hexagram reading.
        """
        original_data = self.get_hexagram_data(original_hex_num)
        resulting_data = self.get_hexagram_data(resulting_hex_num)
        
        return HexagramContext(
            original_hexagram=original_data,
            changing_lines=changing_lines,
            resulting_hexagram=resulting_data
        )
        
    def get_consultation_prompt(self, context: HexagramContext, question: str) -> str:
        """
        Generate a consultation prompt for the AI model.
        
        Args:
            context (HexagramContext): The hexagram reading context.
            question (str): The user's question.
            
        Returns:
            str: A formatted prompt incorporating the context and question.
        """
        # Konstruiere einen strukturierten Prompt
        prompt = [
            f"Frage: {question}\n",
            "Hexagramm-Kontext:",
            f"- Ursprüngliches Hexagramm: {context.original_hexagram['hexagram']['name']}",
            f"- Wandelnde Linien: {', '.join(map(str, context.changing_lines))}",
            f"- Resultierendes Hexagramm: {context.resulting_hexagram['hexagram']['name']}\n",
            "Bitte interpretiere diese Konstellation im Kontext der Frage."
        ]
        
        return "\n".join(prompt)