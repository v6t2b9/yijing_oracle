# yijing/utils/formatting.py

"""
Formatting Module
===============
Provides utilities for formatting I Ching readings and analysis results.

This module contains functions for:
- Converting readings to Markdown format
- Formatting analysis results
- Creating structured consultation responses
"""

from typing import Dict, Any, List
from ..models import HypergramLine, Hypergram, HypergramData
from ..models.contexts import HexagramContext


def generiere_erweiterte_weissagung(linien_werte: List[int]) -> Dict[str, Any]:
    """
    Generiert eine vollständige I Ging Weissagung mit allen verfügbaren Textinformationen.
    Args:
        linien_werte (List[int]): Eine Liste von Integer-Werten, die die Linien des Hypergramms darstellen.
    Returns:
        Dict[str, Any]: Ein Wörterbuch, das die vollständige Weissagung enthält, einschließlich:
            - 'ursprung': Informationen über das ursprüngliche Hexagramm
            - 'wandelnde_linien': Informationen über die wandelnden Linien
            - 'ergebnis': Informationen über das resultierende Hexagramm
    """
    # Hypergramm-Linien erstellen
    linien = [HypergramLine(value=wert) for wert in linien_werte]
    hypergramm = Hypergram(lines=linien)
    
    # Hypergramm-Daten erstellen
    hypergramm_daten = HypergramData(
        hypergram=hypergramm,
        old_hexagram=hypergramm.old_hexagram(),
        new_hexagram=hypergramm.new_hexagram(),
        changing_lines=hypergramm.changing_lines()
    )
    
    # Manager erst hier importieren und initialisieren
    from ..core.manager import HexagramManager
    from pathlib import Path
    resources_dir = Path(__file__).parent.parent / 'resources'
    manager = HexagramManager(resources_dir)
    
    # Hexagramm-Nummern ermitteln
    ursprungs_nummer = hypergramm_daten.old_hexagram.to_binary_number() + 1
    ergebnis_nummer = hypergramm_daten.new_hexagram.to_binary_number() + 1
    
    # Kontext erstellen
    kontext = manager.create_reading_context(
        original_hex_num=ursprungs_nummer,
        changing_lines=[i + 1 for i in hypergramm_daten.changing_lines],
        resulting_hex_num=ergebnis_nummer
    )
    
    return {
        'ursprung': {
            'nummer': ursprungs_nummer,
            'name': kontext.original_hexagram['hexagram']['name'],
            'darstellung': hypergramm_daten.old_hexagram.to_unicode_representation(),
            'trigrams': kontext.original_hexagram['hexagram']['trigrams'],
            'bedeutung': kontext.original_hexagram['hexagram']['meaning'],
            'urteil': kontext.original_hexagram['judgment'],
            'bild': kontext.original_hexagram['image']
        },
        'wandelnde_linien': {
            'positionen': [i + 1 for i in hypergramm_daten.changing_lines],
            'deutungen': kontext.get_relevant_line_interpretations()
        },
        'ergebnis': {
            'nummer': ergebnis_nummer,
            'name': kontext.resulting_hexagram['hexagram']['name'],
            'darstellung': hypergramm_daten.new_hexagram.to_unicode_representation(),
            'trigrams': kontext.resulting_hexagram['hexagram']['trigrams'],
            'bedeutung': kontext.resulting_hexagram['hexagram']['meaning'],
            'urteil': kontext.resulting_hexagram['judgment'],
            'bild': kontext.resulting_hexagram['image']
        }
    }

def formatiere_weissagung_markdown(weissagung: Dict[str, Any]) -> str:
    """Format a complete I Ching reading as Markdown text.
    
    Args:
        weissagung (Dict[str, Any]): Reading data containing:
            - ursprung: Original hexagram information
            - wandelnde_linien: Changing lines information
            - ergebnis: Resulting hexagram information
            
    Returns:
        str: Formatted Markdown text of the reading
    """
    # Die bestehende Implementierung bleibt gleich, nur der Name ändert sich
    ursprung = weissagung['ursprung']
    ergebnis = weissagung['ergebnis']
    
    md = [
        "# I GING WEISSAGUNG\n",
        
        "## URSPRÜNGLICHES HEXAGRAMM\n",
        f"### {ursprung['name']} (Nr. {ursprung['nummer']})\n",
        f"Symbol: {ursprung['darstellung']}\n",
        
        "#### Trigramme\n",
        f"Oben: {ursprung['trigrams']['above']['name']} "
        f"({ursprung['trigrams']['above']['attributes']})\n",
        f"Unten: {ursprung['trigrams']['below']['name']} "
        f"({ursprung['trigrams']['below']['attributes']})\n",
        
        "#### Grundbedeutung\n",
        f"{ursprung['bedeutung']['description']}\n",
        
        "#### Das Urteil\n",
        f"{ursprung['urteil']['description']}\n",
        
        "##### Analyse\n",
        "\n".join([f"- {punkt}" for punkt in ursprung['urteil']['analysis']]) + "\n",
        
        "#### Das Bild\n",
        f"{ursprung['bild']['description']}\n",
        f"**Lehre:** {ursprung['bild']['lesson']}\n",
        
        "## WANDELNDE LINIEN\n"
    ]
    
    for linie in weissagung['wandelnde_linien']['deutungen']:
        md.extend([
            f"### {linie['position']}. Linie\n",
            f"**Text:** {linie['text']}\n",
            f"**Deutung:** {linie['interpretation']}\n"
        ])
    
    md.extend([
        "## RESULTIERENDES HEXAGRAMM\n",
        f"### {ergebnis['name']} (Nr. {ergebnis['nummer']})\n",
        f"Symbol: {ergebnis['darstellung']}\n",
        
        "#### Trigramme\n",
        f"Oben: {ergebnis['trigrams']['above']['name']} "
        f"({ergebnis['trigrams']['above']['attributes']})\n",
        f"Unten: {ergebnis['trigrams']['below']['name']} "
        f"({ergebnis['trigrams']['below']['attributes']})\n",
        
        "#### Grundbedeutung\n",
        f"{ergebnis['bedeutung']['description']}\n",
        
        "#### Das Urteil\n",
        f"{ergebnis['urteil']['description']}\n",
        
        "##### Analyse\n",
        "\n".join([f"- {punkt}" for punkt in ergebnis['urteil']['analysis']]) + "\n",
        
        "#### Das Bild\n",
        f"{ergebnis['bild']['description']}\n",
        f"**Lehre:** {ergebnis['bild']['lesson']}\n"
    ])
    
    return "".join(md)

def format_analyse_markdown(analyse: Dict[str, Any]) -> str:
    """Format hexagram analysis results as Markdown text.
    
    Args:
        analyse (Dict[str, Any]): Analysis data containing transformation details
            and key aspects of the reading
            
    Returns:
        str: Formatted Markdown text of the analysis
    """
    md = [
        "# ANALYSE DER HEXAGRAMM-TRANSFORMATION\n",
        
        "## Trigramm-Transformation\n",
        "### Ursprüngliches Hexagramm\n",
        f"- Oberes Trigramm: {analyse['trigramm_transformation']['ursprung']['oben']['name']} "
        f"({analyse['trigramm_transformation']['ursprung']['oben']['attributes']})\n",
        f"- Unteres Trigramm: {analyse['trigramm_transformation']['ursprung']['unten']['name']} "
        f"({analyse['trigramm_transformation']['ursprung']['unten']['attributes']})\n",
        
        "### Resultierendes Hexagramm\n",
        f"- Oberes Trigramm: {analyse['trigramm_transformation']['ergebnis']['oben']['name']} "
        f"({analyse['trigramm_transformation']['ergebnis']['oben']['attributes']})\n",
        f"- Unteres Trigramm: {analyse['trigramm_transformation']['ergebnis']['unten']['name']} "
        f"({analyse['trigramm_transformation']['ergebnis']['unten']['attributes']})\n",
        
        "## Wandlungslinien\n",
        f"- Anzahl der Wandlungen: {analyse['wandlungslinien_anzahl']}\n",
        f"- Positionen: {', '.join(map(str, analyse['wandlungslinien_positionen']))}\n",
        
        "## Kernaspekte\n",
        "### Ursprüngliches Hexagramm\n",
        f"- Name: {analyse['kernaspekte']['ursprung']['name']}\n",
        f"- Kernelement: {analyse['kernaspekte']['ursprung']['kernelement']}\n",
        
        "### Resultierendes Hexagramm\n",
        f"- Name: {analyse['kernaspekte']['ergebnis']['name']}\n",
        f"- Kernelement: {analyse['kernaspekte']['ergebnis']['kernelement']}\n"
    ]
    
    return "".join(md)
