# yijing/utils/validate_resources.py
"""
Resource Validation Module
========================
Validates JSON resource files against their schemas.
"""

import json
from pathlib import Path
import jsonschema
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

def load_schema(schema_name: str) -> Dict:
    """Load a JSON schema file.
    
    Args:
        schema_name (str): Name of the schema file
        
    Returns:
        Dict: Loaded schema
        
    Raises:
        FileNotFoundError: If schema file not found
    """
    schema_path = Path(__file__).parent.parent / 'resources' / 'schemas' / schema_name
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_hexagram_files() -> List[str]:
    """Validate all hexagram JSON files against schema.
    
    Returns:
        List[str]: List of validation errors
    """
    schema = load_schema('hexagram.schema.json')
    hex_dir = Path(__file__).parent.parent / 'resources' / 'hexagram_json'
    errors = []
    
    for hex_file in hex_dir.glob('*.json'):
        try:
            with open(hex_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            jsonschema.validate(instance=data, schema=schema)
            logger.debug(f"Validated {hex_file.name}")
        except jsonschema.exceptions.ValidationError as e:
            error = f"Validation error in {hex_file.name}: {e.message}"
            errors.append(error)
            logger.error(error)
        except Exception as e:
            error = f"Error processing {hex_file.name}: {str(e)}"
            errors.append(error)
            logger.error(error)
            
    return errors

def validate_all_resources() -> bool:
    """Validate all resource files."""
    return len(validate_hexagram_files()) == 0