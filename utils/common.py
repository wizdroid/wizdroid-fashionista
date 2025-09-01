import json
import random
import re
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


def filter_valid_options(options: List[str]) -> List[str]:
    """
    Filter options to include only valid non-control values.
    
    Args:
        options: List of options to filter
        
    Returns:
        Filtered list with none and random as first options
    """
    if not options:
        return ["none", "random"]
    
    # Remove control values and empty strings, then deduplicate and sort
    valid_options = sorted(list(set(opt for opt in options if opt and opt not in ["none", "random"])))
    
    # Add control values at the beginning
    return ["none", "random"] + valid_options


def apply_preset(current: Dict[str, Any], preset: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply preset values to a current selection dict, only filling in empty or control values.

    Control values considered empty: "", "none", "random".
    """
    result = dict(current)
    for k, v in preset.items():
        cur = result.get(k)
        if cur in (None, "", "none", "random"):
            result[k] = v
    return result


def _split_terms(text: str) -> List[str]:
    """Split a comma/semicolon separated string into normalized terms."""
    if not isinstance(text, str) or not text.strip():
        return []
    raw = [t.strip() for t in text.replace(";", ",").split(",")]
    # dedupe while preserving order
    seen = set()
    terms: List[str] = []
    for t in raw:
        if not t:
            continue
        # normalize simple spacing and lowercase for dedupe purposes
        key = " ".join(t.split()).lower()
        if key in seen:
            continue
        seen.add(key)
        terms.append(t)
    return terms


def clean_comma_separated_terms(text: str) -> str:
    """
    Clean a comma/semicolon separated string: trim, dedupe, and normalize spacing between terms.
    Returns a comma+space separated list or empty string.
    """
    terms = _split_terms(text)
    return ", ".join(terms)


def compose_negative_prompt(user_avoid_terms: str, auto_terms: List[str]) -> str:
    """
    Combine user-provided avoid terms with automatically generated negatives, cleaning duplicates.

    Args:
        user_avoid_terms: Raw string from UI (comma/semicolon separated)
        auto_terms: Additional terms computed by logic

    Returns:
        Cleaned comma-separated negative prompt string
    """
    terms = _split_terms(user_avoid_terms)
    for t in auto_terms:
        if not t:
            continue
        key = " ".join(t.split()).lower()
        # We compare against lower-cased keys of existing terms
        if all(" ".join(x.split()).lower() != key for x in terms):
            terms.append(t)
    return ", ".join(terms)


def extract_outfit_template(preset: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract clothing items from a preset, removing color information.
    
    This function takes a preset and extracts only the clothing items,
    removing color adjectives to create a template that allows for
    random color selection by the AI.
    
    Args:
        preset: Preset dictionary containing outfit information
        
    Returns:
        Dictionary with clothing pieces without color information
    """
    # Define clothing-related body parts (exclude non-clothing items)
    clothing_parts = {
        "torso", "legs", "feet", "headgear", "neck", "ear", "fingers", 
        "hand", "waist", "eyewear", "forearm", "arm"
    }
    
    # Common color adjectives to remove
    color_patterns = [
        # Basic colors
        r'\b(red|blue|green|yellow|orange|purple|pink|black|white|brown|gray|grey)\b',
        # Extended colors
        r'\b(navy|royal|emerald|crimson|scarlet|maroon|burgundy|turquoise|teal|coral|salmon)\b',
        r'\b(beige|tan|khaki|olive|gold|silver|bronze|copper|rose|lavender|violet|indigo)\b',
        # Descriptive colors
        r'\b(dark|light|bright|pale|deep|rich|vibrant|neon|pastel|metallic|matte)\b',
        # Color combinations
        r'\b(multicolor|multicolored|rainbow|striped|checkered|plaid|floral|printed)\b',
        # Material-based colors
        r'\b(denim|leather|suede|silk|cotton|linen|wool|cashmere|velvet|satin)\s*(?=\w)',
    ]
    
    template = {}
    
    for part, item in preset.items():
        if part in clothing_parts and isinstance(item, str) and item.strip():
            # Remove color information using regex patterns
            cleaned_item = item.strip()
            for pattern in color_patterns:
                cleaned_item = re.sub(pattern, '', cleaned_item, flags=re.IGNORECASE)
            
            # Clean up extra spaces and normalize
            cleaned_item = ' '.join(cleaned_item.split())
            
            # Only include if we still have meaningful content
            if cleaned_item and len(cleaned_item) > 2:
                template[part] = cleaned_item
    
    return template


def apply_outfit_template(current: Dict[str, Any], template: Dict[str, str]) -> Dict[str, Any]:
    """
    Apply outfit template to current selection, filling only empty clothing fields.
    
    This differs from apply_preset by only applying clothing items and allowing
    the AI to randomly select colors and other styling.
    
    Args:
        current: Current selection dictionary
        template: Outfit template with clothing items (no colors)
        
    Returns:
        Updated selection with template clothing applied
    """
    result = dict(current)
    
    for part, item in template.items():
        cur = result.get(part)
        # Only apply if current value is empty or control value
        if cur in (None, "", "none", "random"):
            result[part] = item
    
    return result
