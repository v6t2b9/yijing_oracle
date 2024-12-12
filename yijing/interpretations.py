# yijing/interpretations.py

from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class LineInterpretation(BaseModel):
    """Interpretation einer einzelnen Linie eines Hexagramms."""
    position: int = Field(..., ge=1, le=6, description="Position der Linie von unten (1-6)")
    changing: bool = Field(..., description="Ob es sich um eine wandelnde Linie handelt")
    wilhelm_text: str = Field(..., description="Richard Wilhelms Interpretation der Linie")
    symbolic_image: Optional[str] = Field(None, description="Das symbolische Bild der Linie")
    advice: Optional[str] = Field(None, description="Praktischer Rat für diese Linie")
    historical_context: Optional[str] = Field(None, description="Historischer/kultureller Kontext")

class TrigramInterpretation(BaseModel):
    """Interpretation eines Trigrams."""
    name_chinese: str = Field(..., description="Chinesischer Name des Trigrams")
    name_german: str = Field(..., description="Deutscher Name des Trigrams")
    attributes: List[str] = Field(..., description="Attribute und Eigenschaften des Trigrams")
    natural_symbol: str = Field(..., description="Natursymbol des Trigrams")
    family_member: str = Field(..., description="Familienmitglied in der Trigram-Familie")
    direction: str = Field(..., description="Himmelsrichtung des Trigrams")
    wilhelm_text: str = Field(..., description="Richard Wilhelms Interpretation")
    binary_sequence: str = Field(..., description="Binäre Sequenz (000-111)")

class HexagramInterpretation(BaseModel):
    """Vollständige Interpretation eines Hexagramms."""
    number: int = Field(..., ge=1, le=64, description="Nummer des Hexagramms (1-64)")
    name_chinese: str = Field(..., description="Chinesischer Name")
    name_pinyin: str = Field(..., description="Pinyin-Umschrift")
    name_german: str = Field(..., description="Deutscher Name nach Wilhelm")
    binary_sequence: str = Field(..., description="Binäre Sequenz (000000-111111)")
    
    upper_trigram: TrigramInterpretation = Field(..., description="Oberes Trigram")
    lower_trigram: TrigramInterpretation = Field(..., description="Unteres Trigram")
    
    judgement: str = Field(..., description="Das Urteil (Wilhelm)")
    image: str = Field(..., description="Das Bild (Wilhelm)")
    wilhelm_explanation: str = Field(..., description="Wilhelms Erklärung")
    
    lines: List[LineInterpretation] = Field(
        ..., 
        min_items=6, 
        max_items=6, 
        description="Interpretationen der sechs Linien"
    )
    
    nuclear_hexagram: Optional[int] = Field(
        None, 
        description="Nummer des Kernhexagramms (falls relevant)"
    )
    
    associations: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Zugeordnete Symbole und Bedeutungen in verschiedenen Kategorien"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "number": 1,
                "name_chinese": "乾",
                "name_pinyin": "Qián",
                "name_german": "Das Schöpferische",
                "binary_sequence": "111111",
                "upper_trigram": {
                    "name_chinese": "乾",
                    "name_german": "Das Schöpferische",
                    "attributes": ["stark", "schöpferisch", "himmlisch"],
                    "natural_symbol": "Himmel",
                    "family_member": "Vater",
                    "direction": "Nordwesten",
                    "wilhelm_text": "Das Schöpferische wirkt...",
                    "binary_sequence": "111"
                },
                "lower_trigram": {
                    "name_chinese": "乾",
                    "name_german": "Das Schöpferische",
                    "attributes": ["stark", "schöpferisch", "himmlisch"],
                    "natural_symbol": "Himmel",
                    "family_member": "Vater",
                    "direction": "Nordwesten",
                    "wilhelm_text": "Das Schöpferische wirkt...",
                    "binary_sequence": "111"
                },
                "judgement": "Das Schöpferische wirkt erhaben...",
                "image": "Der Himmel ist in Bewegung...",
                "wilhelm_explanation": "Das erste Hexagramm...",
                "lines": [
                    {
                        "position": 1,
                        "changing": False,
                        "wilhelm_text": "Verborgener Drache...",
                        "symbolic_image": "Drache unter der Erde",
                        "advice": "Warten und Kraft sammeln"
                    }
                ],
                "nuclear_hexagram": 2,
                "associations": {
                    "elements": ["Metall", "Himmel"],
                    "animals": ["Drache", "Pferd"],
                    "body_parts": ["Kopf", "Himmel"]
                }
            }
        }

class YijingInterpretations(BaseModel):
    """Sammlung aller Interpretationen des Yijing."""
    trigrams: Dict[str, TrigramInterpretation] = Field(
        ..., 
        description="Sammlung aller 8 Trigramme"
    )
    hexagrams: Dict[int, HexagramInterpretation] = Field(
        ..., 
        description="Sammlung aller 64 Hexagramme"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "trigrams": {
                    "111": {"name_chinese": "乾", "name_german": "Das Schöpferische"}
                },
                "hexagrams": {
                    "1": {"number": 1, "name_chinese": "乾"}
                }
            }
        }

