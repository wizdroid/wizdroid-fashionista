"""
Utility functions for ComfyUI Outfit Selection Node.
This module provides shared utilities for data loading, random selection, and JSON operations.
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def load_json_file(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Load a JSON file with error handling.
    
    Args:
        file_path: Path to the JSON file
        default: Default value to return if loading fails
        
    Returns:
        Parsed JSON data or default value
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        print(f"[ComfyUI-Outfit] Error loading {file_path}: {e}")
        return default if default is not None else {}


def safe_random_choice(options: List[str], exclude: Optional[List[str]] = None) -> str:
    """
    Safely select a random choice from options, excluding specified values.
    
    Args:
        options: List of options to choose from
        exclude: List of values to exclude from selection
        
    Returns:
        Random choice from valid options or "none" if no valid options
    """
    if not options:
        return "none"
    
    exclude = exclude or ["none", "random"]
    valid_options = [opt for opt in options if opt not in exclude]
    
    if not valid_options:
        return "none"
    
    return random.choice(valid_options)


def build_prompt_parts(
    data: Dict[str, Any], 
    mappings: Dict[str, str],
    random_handler: Optional[callable] = None
) -> List[str]:
    """
    Build prompt parts from data dictionary using field mappings.
    
    Args:
        data: Input data dictionary
        mappings: Field name to prompt label mappings
        random_handler: Optional function to handle random selections
        
    Returns:
        List of formatted prompt parts
    """
    parts = []
    
    for field, label in mappings.items():
        value = data.get(field)
        if not value or value == "none":
            continue
            
        if value == "random" and random_handler:
            value = random_handler(field, data)
            
        if value and value != "none":
            parts.append(f"{label}: {value}")
    
    return parts


def validate_data_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate that data contains required fields.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        
    Returns:
        True if all required fields are present, False otherwise
    """
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        print(f"[ComfyUI-Outfit] Missing required fields: {missing_fields}")
        return False
    
    return True


def ensure_list_format(value: Any) -> List[str]:
    """
    Ensure value is in list format for consistent processing.
    
    Args:
        value: Value to convert to list
        
    Returns:
        List representation of the value
    """
    if isinstance(value, list):
        return value
    elif isinstance(value, str):
        return [value] if value else []
    else:
        return []


def filter_valid_options(options: List[str], prefix: str = "none") -> List[str]:
    """
    Filter options to include only valid non-control values.
    
    Args:
        options: List of options to filter
        prefix: Prefix to add to filtered options
        
    Returns:
        Filtered list with none and random as first options
    """
    if not options:
        return ["none", "random"]
    
    # Remove control values and empty strings
    valid_options = [opt for opt in options if opt and opt not in ["none", "random"]]
    
    # Add control values at the beginning
    return ["none", "random"] + valid_options


def deep_merge_dicts(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        base: Base dictionary
        update: Dictionary to merge into base
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters for Windows/Unix filesystems
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    return filename if filename else "unnamed"
