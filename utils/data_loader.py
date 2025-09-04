import json
from pathlib import Path
from typing import Any, Dict, List

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
        data = load_json_file(part_file, {})
        
        attire_items = data.get("attire", [])
        if not isinstance(attire_items, list):
            options[part] = ["none", "random"]
            continue
        
        types = [item["type"] for item in attire_items if isinstance(item, dict) and "type" in item and isinstance(item["type"], str)]
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
    file_path = data_dir / "body_type.json"
    data = load_json_file(file_path, {})
    attire = data.get("attire", [])
    # Ensure we only collect string types to satisfy type checker and runtime safety
    types: List[str] = [
        t for t in (item.get("type") for item in attire if isinstance(item, dict)) if isinstance(t, str)
    ]
    return filter_valid_options(types)


def discover_body_parts(data_dir: Path) -> List[str]:
    """
    Discover available body parts from JSON files in directory.
    
    Args:
        data_dir: Directory to scan for body part files
        
    Returns:
        List of body part names
    """
    if not data_dir.is_dir():
        return []
    
    excluded_files = {"body_type.json", "poses.json"}
    
    return sorted([
        f.stem for f in data_dir.iterdir()
        if f.is_file() and f.suffix == ".json" and f.name not in excluded_files
    ])


def discover_genders(outfit_data_dir: Path) -> List[str]:
    """
    Discover available gender folders.
    
    Args:
        outfit_data_dir: Base outfit data directory
        
    Returns:
        List of gender folder names
    """
    if not outfit_data_dir.is_dir():
        return []
    
    return sorted([f.name for f in outfit_data_dir.iterdir() if f.is_dir()])


def load_scene_highlights(styles_dir: Path) -> Dict[str, List[str]]:
    """
    Load scene highlight options: moods, times, weather, color_schemes.

    Args:
        styles_dir: Directory containing styles JSON files

    Returns:
        Dict with keys: moods, times, weather, color_schemes
    """
    file_path = styles_dir / "scene_highlights.json"
    data = load_json_file(file_path, {})
    result: Dict[str, List[str]] = {}
    for key in ("moods", "times", "weather", "color_schemes"):
        options = data.get(key, [])
        result[key] = filter_valid_options(options if isinstance(options, list) else [])
    return result


def load_description_styles(styles_dir: Path) -> List[str]:
    """
    Load available description prompt styles (e.g., sdxl, flux).
    """
    file_path = styles_dir / "description_prompts.json"
    data = load_json_file(file_path, {})
    if isinstance(data, dict):
        return filter_valid_options(list(data.keys()))
    return ["none", "random"]


def load_scale_options(styles_dir: Path) -> List[str]:
    """
    Load available creative/detail scale options from scale_instructions.json.
    """
    file_path = styles_dir / "scale_instructions.json"
    data = load_json_file(file_path, {})
    if isinstance(data, dict):
        return filter_valid_options(list(data.keys()))
    return ["none", "random"]


def load_presets(data_dir: Path) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Load presets from data/presets.json structured as {gender: {preset_name: mappings}}.

    Returns a dict mapping gender to preset name to field:value mapping.
    """
    file_path = data_dir / "presets.json"
    data = load_json_file(file_path, {})
    return data if isinstance(data, dict) else {}


def load_gender_presets(gender_data_dir: Path) -> Dict[str, Dict[str, str]]:
    """
    Load presets for a specific gender from outfit/{gender}/presets.json.
    
    Args:
        gender_data_dir: Directory containing gender-specific outfit data (e.g., data/outfit/female)
        
    Returns:
        Dictionary mapping preset names to their field values
    """
    file_path = gender_data_dir / "presets.json"
    data = load_json_file(file_path, {})
    return data if isinstance(data, dict) else {}