# yijing/utils.py
from pathlib import Path
from typing import Optional
from .enums import ConsultationMode

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