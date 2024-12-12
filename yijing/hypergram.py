# hypergram.py - Enthält Funktionen zur Erstellung und Handhabung des Hypergramms
import random
from .models import Hypergram, HypergramData, HypergramLine
import logging

# Konfiguriere Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Funktion zur Erzeugung eines neuen Hypergramms
def cast_hypergram() -> HypergramData:
    """
    Erzeugt ein Hypergramm bestehend aus 6 Linien, wobei jede Linie einen Zufallswert von 6, 7, 8 oder 9 hat.

    Diese Funktion erstellt ein Hypergram-Objekt mit 6 zufällig generierten Linien. Jede Linie ist eine
    Instanz von HypergramLine mit einem Zufallswert aus 6, 7, 8 oder 9. Anschließend wird ein 
    HypergramData-Objekt konstruiert, das das generierte Hypergramm sowie die entsprechenden alten 
    und neuen Hexagramme und die sich verändernden Linien enthält.

    Returns:
        HypergramData: Ein HypergramData-Objekt mit dem generierten Hypergramm und zugehörigen Hexagrammen    
    """
    # Erzeugt 6 Linien für das Hypergramm, wobei jede Linie einen der Werte 6, 7, 8 oder 9 haben kann
    logger.debug("Erzeuge 6 Hypergrammlinien mit zufälligen Werten 6, 7, 8 oder 9")
    lines = [HypergramLine(value=random.choice([6, 7, 8, 9])) for _ in range(6)] # Erzeugt 6 Linien mit zufälligen Werten
    logger.debug(f"Generierte Linien: {[line.value for line in lines]}")
    logger.debug("Erzeuge Hypergramm-Objekt mit den generierten Linien")
    hypergram = Hypergram(lines=lines) # Erzeugt ein Hypergramm-Objekt mit den generierten Linien
    logger.debug(f"Generiertes Hypergramm: {hypergram}")
    # Erstellt ein HypergramData-Objekt, das das Hypergramm und die beiden zugehörigen Hexagramme enthält
    logger.debug("Erstelle HypergramData-Objekt mit altem und neuem Hexagramm")
    logger.debug(f"Altes Hexagramm: {hypergram.old_hexagram()}")
    logger.debug(f"Neues Hexagramm: {hypergram.new_hexagram()}")
    logger.debug(f"Sich verändernde Linien: {hypergram.changing_lines()}")
    return HypergramData(
        hypergram=hypergram, # Das generierte Hypergramm, z.B. [6, 7, 8, 9, 6, 7]
        old_hexagram=hypergram.old_hexagram(), # Das alte Hexagramm, z.B. [1, 1, 2, 2, 1, 1]
        new_hexagram=hypergram.new_hexagram(), # Das neue Hexagramm, z.B. [1, 2, 2, 2, 1, 2]
        changing_lines=hypergram.changing_lines() # Die sich verändernden Linien, z.B. [1, 5]
    )
