"""YAML Parser for CV Builder.

This module handles the parsing of YAML files containing CV data.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from pydantic import ValidationError

from ..models import CV


def parse_yaml_file(file_path: str) -> Dict[str, Any]:
    """Parse a YAML file and return its contents as a dictionary.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Dict containing the parsed YAML data
        
    Raises:
        FileNotFoundError: If the file does not exist
        yaml.YAMLError: If the file cannot be parsed as YAML
    """
    yaml_path = Path(file_path)
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as yaml_file:
            data = yaml.safe_load(yaml_file)
        return data
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file: {e}")


def validate_cv_data(data: Dict[str, Any]) -> CV:
    """Validates that the CV data is properly structured using Pydantic models.
    
    Args:
        data: Dictionary containing CV data
        
    Returns:
        CV object if data is valid, or a list of validation errors if invalid
    """
    try:
        cv = CV.model_validate(data)
        return cv
    except ValidationError as e:
        raise ValidationError(f"Validation error: {e.errors()}")