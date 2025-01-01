# coverage_analysis.py

import subprocess
import sys
from pathlib import Path

# coverage_analysis.py
def run_coverage_analysis():
    """Run tests with coverage analysis."""
    subprocess.run(
        ["pytest", "--cov=yijing", "--cov-report=term-missing"],
        check=True
    )

if __name__ == "__main__":
    run_coverage_analysis()