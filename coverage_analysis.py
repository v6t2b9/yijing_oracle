# coverage_analysis.py

import subprocess
import sys
from pathlib import Path

def run_coverage_analysis():
    """Führt Tests aus und analysiert die Testabdeckung."""
    try:
        # Führe Tests mit Coverage aus
        result = subprocess.run(
            ["pytest", "--cov=yijing", "--cov-report=term-missing"],
            capture_output=True,
            text=True
        )
        
        print("Test-Ergebnisse:")
        print(result.stdout)
        
        if result.stderr:
            print("\nFehler und Warnungen:")
            print(result.stderr)
            
        # Analysiere Coverage-Report
        coverage_data = parse_coverage_output(result.stdout)
        
        print("\nTestabdeckungs-Analyse:")
        print("------------------------")
        for module, stats in coverage_data.items():
            print(f"\nModul: {module}")
            print(f"Gesamtabdeckung: {stats['coverage']}%")
            print(f"Fehlende Zeilen: {stats['missing_lines']}")
            
        # Identifiziere kritische Bereiche
        identify_critical_areas(coverage_data)
        
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei der Testausführung: {e}")
        sys.exit(1)

def parse_coverage_output(output: str) -> dict:
    """Analysiert die Coverage-Ausgabe und extrahiert relevante Informationen."""
    coverage_data = {}
    
    # Implementiere hier die Parsing-Logik für das Coverage-Output
    # Dies ist ein vereinfachtes Beispiel
    for line in output.split('\n'):
        if 'yijing' in line and '%' in line:
            parts = line.split()
            module = parts[0]
            coverage = int(parts[-1].rstrip('%'))
            missing = parts[-2] if len(parts) > 2 else ""
            
            coverage_data[module] = {
                'coverage': coverage,
                'missing_lines': missing
            }
    
    return coverage_data

def identify_critical_areas(coverage_data: dict):
    """Identifiziert kritische Bereiche mit niedriger Testabdeckung."""
    print("\nKritische Bereiche:")
    print("------------------")
    
    for module, stats in coverage_data.items():
        if stats['coverage'] < 80:
            print(f"\n{module}:")
            print(f"- Niedrige Abdeckung: {stats['coverage']}%")
            print(f"- Fehlende Zeilen: {stats['missing_lines']}")
            print("- Empfehlung: Zusätzliche Tests für fehlende Zeilen erstellen")
            
        if stats['coverage'] < 60:
            print("- KRITISCH: Sehr niedrige Testabdeckung!")
            print("- Sofortige Aufmerksamkeit erforderlich")

if __name__ == "__main__":
    run_coverage_analysis()