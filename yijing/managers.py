# yijing/managers.py

from pathlib import Path
from typing import Dict, Any, List
from functools import lru_cache
import json
from .models import ConsultationPrompt, HexagramContext

class HexagramManager:
    """Manages hexagram data and consultation prompts."""
    
    def __init__(self, resources_path: Path):
        self.resources_path = resources_path / 'hexagram_json'
        if not self.resources_path.exists():
            raise FileNotFoundError(f"Hexagram resources directory not found: {self.resources_path}")
    
    @lru_cache(maxsize=64)
    def load_hexagram(self, hexagram_number: int) -> Dict[str, Any]:
        """Loads a specific hexagram's data with caching."""
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
        """Creates a detailed consultation prompt for the oracle.
        
        This method formats the hexagram data and question into a structured prompt
        that follows the I Ching consultation format.
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