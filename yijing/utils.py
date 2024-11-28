# yijing/utils.py
from pathlib import Path
from typing import Optional

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