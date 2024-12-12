# yijing/managers.py

from pathlib import Path
from typing import Dict, Any, List
from functools import lru_cache
import json
from .models import ConsultationPrompt, HexagramContext

class HexagramManager:
    """Manages the loading and interpretation of I Ching hexagrams and their readings.
    This class handles loading hexagram data from JSON files, creating reading contexts,
    and generating consultation prompts for I Ching divination. It implements caching
    for efficient hexagram data retrieval.
    Attributes:
        resources_path (Path): Path to the directory containing hexagram JSON files.
    Methods:
        load_hexagram(hexagram_number: int) -> Dict[str, Any]:
            Loads and caches hexagram data from JSON files.
        create_reading_context(original_hex_num: int, changing_lines: List[int], 
            Creates a complete context object for a hexagram reading.
        get_consultation_prompt(context: HexagramContext, question: str) -> str:
            Generates a structured consultation prompt for I Ching interpretation.
    Raises:
        FileNotFoundError: If the hexagram resources directory or specific hexagram 
                          files are not found.
    Example:
        manager = HexagramManager(Path("resources"))
        context = manager.create_reading_context(1, [3, 6], 2)
        prompt = manager.get_consultation_prompt(context, "Should I change jobs?")
    """
    
    def __init__(self, resources_path: Path):
        self.resources_path = resources_path / 'hexagram_json'
        if not self.resources_path.exists():
            raise FileNotFoundError(f"Hexagram resources directory not found: {self.resources_path}")
    
    @lru_cache(maxsize=64)
    def load_hexagram(self, hexagram_number: int) -> Dict[str, Any]:
        """Loads a specific hexagram's data with caching.
        Args:
            hexagram_number (int): The number of the hexagram to load (1-64)
        Returns:
            Dict[str, Any]: A dictionary containing the hexagram data with properties like
                name, description, interpretation etc.
        Raises:
            FileNotFoundError: If the hexagram file does not exist in the resources directory
        Example:
            >>> manager.load_hexagram(1)
            {'name': '乾 (qián)', 'description': 'The Creative', ...}
        """
        hexagram_file = self.resources_path / f'hexagram_{hexagram_number:02d}.json'
        
        if not hexagram_file.exists():
            raise FileNotFoundError(f"Hexagram file not found: {hexagram_file}")
            
        with open(hexagram_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_reading_context(self, 
                             original_hex_num: int, 
                             changing_lines: List[int], 
                             resulting_hex_num: int) -> HexagramContext:
        """Creates a complete context for a hexagram reading."""
        return HexagramContext(
            original_hexagram=self.load_hexagram(original_hex_num),
            changing_lines=changing_lines,
            resulting_hexagram=self.load_hexagram(resulting_hex_num)
        )

    def get_consultation_prompt(self, context: HexagramContext, question: str) -> str:
        """Creates a detailed consultation prompt for the I Ching oracle consultation.
        This method formats the hexagram context data and the user's question into a structured
        prompt that follows traditional I Ching consultation format. The prompt includes the original
        hexagram, changing lines, and resulting hexagram, along with their interpretations and 
        guidance for providing consultation advice.
        Args:
            context (HexagramContext): Object containing the original hexagram, resulting hexagram,
                and changing line information for the consultation.
            question (str): The question or concern posed by the person seeking guidance.
        Returns:
            str: A formatted prompt string containing all relevant hexagram information and 
                consultation instructions in German language. The prompt is structured with:
                - Original question
                - Initial situation (original hexagram)
                - Changing lines and their interpretations
                - Future tendency (resulting hexagram)
                - Consultation instructions for interpretation
        Example:
            >>> context = HexagramContext(original_hex, resulting_hex, changing_lines)
            >>> prompt = get_consultation_prompt(context, "Should I change my career?")
            >>> print(prompt)  # Returns formatted consultation text in German
        """
        original_hex = context.original_hexagram
        resulting_hex = context.resulting_hexagram
        
        changing_lines_text = "\n".join([
            f"Linie {line['position']}: {line['text']}\n"
            f"Interpretation: {line['interpretation']}\n"
            for line in context.get_relevant_line_interpretations()
        ])
        
        return f"""Beratungsanfrage: {question}

AUSGANGSSITUATION - {original_hex['hexagram']['name']}

================================================================================

Grundbedeutung:
{original_hex['hexagram']['meaning']['description']}

Das Urteil:
{original_hex['judgment']['description']}

Das Bild:
{original_hex['image']['description']}

WANDELNDE LINIEN

================================================================================

{changing_lines_text}

ZUKÜNFTIGE TENDENZ - {resulting_hex['hexagram']['name']}

================================================================================

Grundbedeutung:
{resulting_hex['hexagram']['meaning']['description']}

Das Urteil:
{resulting_hex['judgment']['description']}

Das Bild:
{resulting_hex['image']['description']}

================================================================================

ANWEISUNG FÜR DIE BERATUNG:

Als weises I Ging Orakel wird um eine tiefgründige Interpretation und Beratung gebeten.
Bitte berücksichtige in deiner Antwort:

1. Die gegenwärtige Situation, wie sie sich im Ausgangshexagramm zeigt
2. Die bedeutsamen Wandlungen, die durch die sich verändernden Linien angezeigt werden
3. Die sich entwickelnde Tendenz, wie sie im resultierenden Hexagramm erscheint
4. Konkrete und praktische Handlungsempfehlungen für die ratsuchende Person

Formuliere die Antwort in einem weisen, aber verständlichen Ton. Beziehe dich auf die 
traditionellen Bilder und Symbole des I Ging, aber übersetze ihre Bedeutung in den 
modernen Kontext der fragenden Person.
"""