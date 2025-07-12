"""
Data loading utilities for ComfyUI Outfit Selection Node.
Handles loading and processing of outfit data files.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .common import filter_valid_options, load_json_file


def load_outfit_data(data_dir: Path, body_parts: List[str]) -> Dict[str, List[str]]:
    """
    Load outfit data for all body parts.
    
    Args:
        data_dir: Directory containing outfit data files
        body_parts: List of body part names to load
        
    Returns:
        Dictionary mapping body parts to their options
    """
    options = {}
    
    for part in body_parts:
        part_file = data_dir / f"{part}.json"
        if not part_file.exists():
            options[part] = ["none", "random"]
            continue
        
        data = load_json_file(part_file, {})
        if not data:
            options[part] = ["none", "random"]
            continue
        
        # Extract types from attire data
        attire_items = data.get("attire", [])
        if not isinstance(attire_items, list):
            options[part] = ["none", "random"]
            continue
        
        types = []
        for item in attire_items:
            if isinstance(item, dict) and "type" in item:
                types.append(item["type"])
            elif isinstance(item, str):
                types.append(item)
        
        options[part] = filter_valid_options(types)
    
    return options


def load_global_options(data_dir: Path, filename: str, key: str) -> List[str]:
    """
    Load global options from a JSON file.
    
    Args:
        data_dir: Base data directory
        filename: Name of the JSON file
        key: Key to extract from JSON data
        
    Returns:
        List of options
    """
    file_path = data_dir / filename
    data = load_json_file(file_path, {})
    
    if not data:
        return ["none", "random"]
    
    options = data.get(key, [])
    if not isinstance(options, list):
        return ["none", "random"]
    
    return filter_valid_options(options)


def load_body_types(data_dir: Path) -> List[str]:
    """
    Load body types from body_type.json.
    
    Args:
        data_dir: Directory containing body type data
        
    Returns:
        List of body type options
    """
    return load_global_options(data_dir, "body_type.json", "attire")


def load_makeup_options(data_dir: Path) -> List[str]:
    """
    Load makeup options from makeup.json.
    
    Args:
        data_dir: Directory containing makeup data
        
    Returns:
        List of makeup options
    """
    file_path = data_dir / "makeup.json"
    data = load_json_file(file_path, {})
    
    if not data:
        return ["none"]
    
    attire_items = data.get("attire", [])
    if not isinstance(attire_items, list):
        return ["none"]
    
    types = []
    for item in attire_items:
        if isinstance(item, dict) and "type" in item:
            types.append(item["type"])
    
    return ["none"] + types


def discover_body_parts(data_dir: Path) -> List[str]:
    """
    Discover available body parts from JSON files in directory.
    
    Args:
        data_dir: Directory to scan for body part files
        
    Returns:
        List of body part names
    """
    if not data_dir.exists():
        return []
    
    excluded_files = {"body_type.json", "poses.json"}
    
    files = [
        f.stem for f in data_dir.iterdir()
        if f.is_file() and f.suffix == ".json" and f.name not in excluded_files
    ]
    
    return sorted(files)


def discover_genders(outfit_data_dir: Path) -> List[str]:
    """
    Discover available gender folders.
    
    Args:
        outfit_data_dir: Base outfit data directory
        
    Returns:
        List of gender folder names
    """
    if not outfit_data_dir.exists():
        return []
    
    return [f.name for f in outfit_data_dir.iterdir() if f.is_dir()]


def validate_data_integrity(data_dir: Path, required_files: List[str]) -> bool:
    """
    Validate that all required data files exist and are valid JSON.
    
    Args:
        data_dir: Directory containing data files
        required_files: List of required file names
        
    Returns:
        True if all files are valid, False otherwise
    """
    for filename in required_files:
        file_path = data_dir / filename
        
        if not file_path.exists():
            print(f"[ComfyUI-Outfit] Missing required file: {filename}")
            return False
        
        data = load_json_file(file_path)
        if data is None:
            print(f"[ComfyUI-Outfit] Invalid JSON in file: {filename}")
            return False
    
    return True


def cache_data_loader(cache_dict: Dict[str, Any]):
    """
    Decorator to cache loaded data to avoid repeated file I/O.
    
    Args:
        cache_dict: Dictionary to use for caching
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            if cache_key in cache_dict:
                return cache_dict[cache_key]
            
            result = func(*args, **kwargs)
            cache_dict[cache_key] = result
            return result
        
        return wrapper
    return decorator
