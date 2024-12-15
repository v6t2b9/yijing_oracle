# yijing/core/manager.py

"""
Manages hexagram data and context for I Ching readings.

This class handles:
- Loading hexagram data from JSON files
- Creating reading contexts
- Generating consultation prompts
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from ..models.contexts import HexagramContext
from .loader import load_hexagram_data  # Geändert von utils zu core

logger = logging.getLogger(__name__)

# Rest der HexagramManager-Klasse bleibt gleich

class HexagramManager:
    """
    Manages hexagram data and context for I Ching readings.
    
    This class handles:
    - Loading hexagram data from JSON files
    - Creating reading contexts
    - Generating consultation prompts
    """
    
    def __init__(self, resources_path: Path):
        """
        Initialize the HexagramManager.
        
        Args:
            resources_path (Path): Path to the resources directory containing hexagram data
        """
        self.resources_path = resources_path
        logger.debug(f"Initialized HexagramManager with resources path: {resources_path}")

    def get_hexagram_data(self, number: int) -> Dict[str, Any]:
        """
        Load data for a specific hexagram.
        
        Args:
            number (int): Hexagram number (1-64)
            
        Returns:
            Dict[str, Any]: Complete hexagram data
            
        Raises:
            ValueError: If hexagram number is invalid
            FileNotFoundError: If hexagram data file not found
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
        Create a complete reading context from hexagram numbers and changing lines.
        
        Args:
            original_hex_num (int): Number of the original hexagram (1-64)
            changing_lines (List[int]): List of changing line indices (0-based)
            resulting_hex_num (int): Number of the resulting hexagram (1-64)
            
        Returns:
            HexagramContext: Complete context for the reading
            
        Raises:
            ValueError: If any input numbers are invalid
        """
        logger.debug(
            f"Creating reading context: original={original_hex_num}, "
            f"changing={changing_lines}, resulting={resulting_hex_num}"
        )
        
        # Validate inputs
        if not (1 <= original_hex_num <= 64 and 1 <= resulting_hex_num <= 64):
            raise ValueError("Invalid hexagram numbers")
            
        # Load hexagram data
        original_data = self.get_hexagram_data(original_hex_num)
        resulting_data = self.get_hexagram_data(resulting_hex_num)
        
        # Convert changing lines to 1-based for consistency with texts
        changing_lines_1based = [i + 1 for i in changing_lines]
        
        return HexagramContext(
            original_hexagram=original_data,
            changing_lines=changing_lines_1based,
            resulting_hexagram=resulting_data
        )

    def get_consultation_prompt(
        self,
        context: HexagramContext,
        question: str
    ) -> str:
        """
        Generate a consultation prompt from context and question.
        
        Args:
            context (HexagramContext): The reading context
            question (str): The question being asked
            
        Returns:
            str: Formatted consultation prompt
        """
        logger.debug(f"Generating consultation prompt for question: {question}")
        
        # Get line interpretations for changing lines
        line_interpretations = context.get_relevant_line_interpretations()
        
        # Format the changing lines section
        changing_lines_text = "\n\n".join([
            f"Position {line['position']}:\n"
            f"Text: {line['text']}\n"
            f"Interpretation: {line['interpretation']}"
            for line in line_interpretations
        ])
        
        # Format the complete prompt
        prompt = f"""
BERATUNG ZUM I GING
==================

FRAGE:
{question}

URSPRÜNGLICHES HEXAGRAMM:
{context.original_hexagram['hexagram']['name']}

Bedeutung:
{context.original_hexagram['hexagram']['meaning']['description']}

Urteil:
{context.original_hexagram['judgment']['description']}

WANDELNDE LINIEN:
{changing_lines_text}

RESULTIERENDES HEXAGRAMM:
{context.resulting_hexagram['hexagram']['name']}

Bedeutung:
{context.resulting_hexagram['hexagram']['meaning']['description']}

Urteil:
{context.resulting_hexagram['judgment']['description']}
"""
        
        return prompt