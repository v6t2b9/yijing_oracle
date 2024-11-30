# yijing/utils.py
from pathlib import Path
from typing import Optional
from .enums import ConsultationMode

import json
from typing import Dict
from .interpretations import YijingInterpretations, TrigramInterpretation, HexagramInterpretation

def load_interpretations() -> YijingInterpretations:
    """
    Lädt die Yijing-Interpretationen aus den JSON-Dateien.
    
    Returns:
        YijingInterpretations: Gesamte Sammlung der Interpretationen
    
    Raises:
        FileNotFoundError: Wenn die Interpretationsdateien nicht gefunden werden
        JSONDecodeError: Wenn die JSON-Dateien nicht valide sind
    """
    resources_dir = Path(__file__).parent / 'resources'
    
    # Lade Trigram-Interpretationen
    trigrams_file = resources_dir / 'trigrams.json'
    if not trigrams_file.exists():
        raise FileNotFoundError(f"Trigram-Datei nicht gefunden: {trigrams_file}")
    
    with open(trigrams_file, 'r', encoding='utf-8') as f:
        trigrams_data = json.load(f)
        trigrams = {
            key: TrigramInterpretation(**value)
            for key, value in trigrams_data.items()
        }
    
    # Lade Hexagramm-Interpretationen
    hexagrams_file = resources_dir / 'hexagrams.json'
    if not hexagrams_file.exists():
        raise FileNotFoundError(f"Hexagramm-Datei nicht gefunden: {hexagrams_file}")
    
    with open(hexagrams_file, 'r', encoding='utf-8') as f:
        hexagrams_data = json.load(f)
        hexagrams = {
            int(key): HexagramInterpretation(**value)
            for key, value in hexagrams_data.items()
        }
    
    return YijingInterpretations(trigrams=trigrams, hexagrams=hexagrams)

def create_interpretation_template() -> Dict:
    """
    Erstellt eine Vorlage für die JSON-Struktur der Interpretationen.
    
    Returns:
        Dict: Template-Struktur für Trigrame und Hexagramme
    """
    template = {
        "trigrams": {
            "000": {
                "name_chinese": "",
                "name_german": "",
                "attributes": [],
                "natural_symbol": "",
                "family_member": "",
                "direction": "",
                "wilhelm_text": "",
                "binary_sequence": "000"
            }
        },
        "hexagrams": {
            "1": {
                "number": 1,
                "name_chinese": "",
                "name_pinyin": "",
                "name_german": "",
                "binary_sequence": "",
                "upper_trigram": {},  # Referenz auf Trigram
                "lower_trigram": {},  # Referenz auf Trigram
                "judgement": "",
                "image": "",
                "wilhelm_explanation": "",
                "lines": [
                    {
                        "position": i,
                        "changing": False,
                        "wilhelm_text": "",
                        "symbolic_image": "",
                        "advice": "",
                        "historical_context": ""
                    } for i in range(1, 7)
                ],
                "nuclear_hexagram": None,
                "associations": {
                    "elements": [],
                    "animals": [],
                    "body_parts": []
                }
            }
        }
    }
    
    return template


def load_yijing_text() -> str:
    """
    Load the Yijing text content from the resources directory.
    
    Returns:
        str: The complete text content of the Yijing
    
    Raises:
        FileNotFoundError: If the yijing.txt file cannot be found
    """
    resources_dir = Path(__file__).parent / 'resources'
    yijing_file = resources_dir / 'yijing.txt'
    
    if not yijing_file.exists():
        raise FileNotFoundError(
            f"Yijing text file not found at {yijing_file}. "
            "Please ensure the file exists in the resources directory."
        )
    
    return yijing_file.read_text(encoding='utf-8')

def load_system_prompt(mode: ConsultationMode) -> str:
    """
    Load the appropriate system prompt based on consultation mode.
    
    Args:
        mode (ConsultationMode): The consultation mode (SINGLE or DIALOGUE)
    
    Returns:
        str: The system prompt content
    
    Raises:
        FileNotFoundError: If the prompt file cannot be found
        ValueError: If an invalid consultation mode is provided
    """
    resources_dir = Path(__file__).parent / 'resources'
    
    # Map consultation modes to their respective prompt files
    prompt_files = {
        ConsultationMode.SINGLE: 'single_system_prompt.txt',
        ConsultationMode.DIALOGUE: 'dialogue_system_prompt.txt'
    }
    
    # Get the correct prompt file for the mode
    prompt_file = resources_dir / prompt_files[mode]
    
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"System prompt file not found at {prompt_file}. "
            "Please ensure the file exists in the resources directory."
        )
    
    return prompt_file.read_text(encoding='utf-8')