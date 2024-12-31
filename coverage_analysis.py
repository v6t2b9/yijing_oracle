# coverage_analysis.py

import subprocess
import sys
from pathlib import Path

def run_coverage_analysis():
    """Führt Tests aus und analysiert die Testabdeckung."""
    try:
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
            
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei der Testausführung: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_coverage_analysis()