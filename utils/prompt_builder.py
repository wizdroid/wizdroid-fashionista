"""
Prompt generation utilities for ComfyUI Outfit Selection Node.
Handles prompt formatting and generation logic.
"""

import random
from typing import Any, Dict, List, Optional, Tuple

from .common import safe_random_choice


class PromptBuilder:
    """
    Builder class for generating formatted prompts from outfit data.
    """
    
    def __init__(self, gender: str):
        """
        Initialize prompt builder for specific gender.
        
        Args:
            gender: Gender identifier (male/female/etc.)
        """
        self.gender = gender
        self.parts = []
        self.random_handlers = {}
    
    def add_character_info(self, name: str, age_group: str, race: str, body_type: str, 
                          age_options: List[str], race_options: List[str], 
                          body_type_options: List[str]) -> 'PromptBuilder':
        """
        Add character information to prompt.
        
        Args:
            name: Character name
            age_group: Age group selection
            race: Race selection
            body_type: Body type selection
            age_options: Available age options
            race_options: Available race options
            body_type_options: Available body type options
            
        Returns:
            Self for method chaining
        """
        if name.strip():
            self.parts.append(f"Character: {name.strip()}")
        
        if age_group != "none":
            if age_group == "random":
                age_group = safe_random_choice(age_options)
            if age_group != "none":
                self.parts.append(f"Age: {age_group}")
        
        if race != "none":
            if race == "random":
                race = safe_random_choice(race_options)
            if race != "none":
                self.parts.append(f"Race: {race}")
        
        if body_type != "none":
            if body_type == "random":
                body_type = safe_random_choice(body_type_options)
            if body_type != "none":
                self.parts.append(f"Body type: {body_type}")
        
        return self
    
    def add_attire(self, attire_data: Dict[str, Any], attire_options: Dict[str, List[str]]) -> 'PromptBuilder':
        """
        Add attire information to prompt.
        
        Args:
            attire_data: Dictionary of attire selections
            attire_options: Available options for each attire part
            
        Returns:
            Self for method chaining
        """
        attire_parts = []
        
        for part, options in attire_options.items():
            if part == "makeup":  # Handle makeup separately
                continue
                
            value = attire_data.get(part, "none")
            if value == "none":
                continue
            elif value == "random":
                value = safe_random_choice(options)
            
            if value != "none":
                attire_parts.append(f"{part}: {value}")
        
        if attire_parts:
            self.parts.append("Attire: " + ", ".join(attire_parts))
        
        return self
    
    def add_makeup(self, makeup_data: str, makeup_options: List[str]) -> 'PromptBuilder':
        """
        Add makeup information to prompt.
        
        Args:
            makeup_data: JSON string containing makeup selections
            makeup_options: Available makeup options
            
        Returns:
            Self for method chaining
        """
        makeup_parts = []
        
        if makeup_data:
            try:
                import json
                makeup_items = json.loads(makeup_data)
                
                for item in makeup_items:
                    if not isinstance(item, dict):
                        continue
                    
                    if not item.get("enabled", True):
                        continue
                    
                    makeup_type = item.get("type")
                    if not makeup_type or makeup_type == "none":
                        continue
                    
                    intensity = item.get("intensity", "medium")
                    color = item.get("color", "none")
                    
                    if color and color != "none":
                        makeup_parts.append(f"{makeup_type} ({color}, {intensity})")
                    else:
                        makeup_parts.append(f"{makeup_type} ({intensity})")
                        
            except (json.JSONDecodeError, TypeError) as e:
                print(f"[{self.gender.capitalize()}OutfitNode] Error parsing makeup data: {e}")
        
        if makeup_parts:
            self.parts.append("Makeup: " + ", ".join(makeup_parts))
        
        return self
    
    def add_pose_and_background(self, pose: str, background: str, 
                               pose_options: List[str], background_options: List[str]) -> 'PromptBuilder':
        """
        Add pose and background information to prompt.
        
        Args:
            pose: Pose selection
            background: Background selection
            pose_options: Available pose options
            background_options: Available background options
            
        Returns:
            Self for method chaining
        """
        if pose != "none":
            if pose == "random":
                pose = safe_random_choice(pose_options)
            if pose != "none":
                self.parts.append(f"Pose: {pose}")
        
        if background != "none":
            if background == "random":
                background = safe_random_choice(background_options)
            if background != "none":
                self.parts.append(f"Background: {background}")
        
        return self
    
    def add_custom_attributes(self, custom_attributes: str) -> 'PromptBuilder':
        """
        Add custom attributes to prompt.
        
        Args:
            custom_attributes: Custom attribute string
            
        Returns:
            Self for method chaining
        """
        if custom_attributes.strip():
            self.parts.append(f"Additional: {custom_attributes.strip()}")
        
        return self
    
    def build(self) -> str:
        """
        Build the final prompt string.
        
        Returns:
            Formatted prompt string
        """
        return ", ".join(self.parts)
    
    def reset(self) -> 'PromptBuilder':
        """
        Reset the builder for reuse.
        
        Returns:
            Self for method chaining
        """
        self.parts.clear()
        return self


def generate_outfit_prompt(gender: str, **kwargs) -> str:
    """
    Generate outfit prompt using the builder pattern.
    
    Args:
        gender: Gender identifier
        **kwargs: All prompt generation parameters
        
    Returns:
        Generated prompt string
    """
    builder = PromptBuilder(gender)
    
    # Extract parameters
    character_name = kwargs.get("character_name", "")
    age_group = kwargs.get("age_group", "none")
    race = kwargs.get("race", "none")
    body_type = kwargs.get("body_type", "none")
    custom_attributes = kwargs.get("custom_attributes", "")
    makeup_data = kwargs.get("makeup_data", "")
    pose = kwargs.get("pose", "none")
    background = kwargs.get("background", "none")
    
    # Extract options
    age_options = kwargs.get("age_options", [])
    race_options = kwargs.get("race_options", [])
    body_type_options = kwargs.get("body_type_options", [])
    attire_options = kwargs.get("attire_options", {})
    makeup_options = kwargs.get("makeup_options", [])
    pose_options = kwargs.get("pose_options", [])
    background_options = kwargs.get("background_options", [])
    
    # Build prompt
    prompt = (builder
              .add_character_info(character_name, age_group, race, body_type,
                                age_options, race_options, body_type_options)
              .add_attire(kwargs, attire_options)
              .add_makeup(makeup_data, makeup_options)
              .add_pose_and_background(pose, background, pose_options, background_options)
              .add_custom_attributes(custom_attributes)
              .build())
    
    return prompt


def create_seed_manager():
    """
    Create a seed manager for handling different seed modes.
    
    Returns:
        Dictionary with seed handling functions
    """
    def handle_fixed_seed(seed: int, **kwargs) -> int:
        """Handle fixed seed mode."""
        return seed
    
    def handle_random_seed(seed: int, **kwargs) -> int:
        """Handle random seed mode."""
        import secrets
        return int.from_bytes(secrets.token_bytes(4), "big")
    
    def handle_increment_seed(seed: int, last_seed: int = 0, **kwargs) -> int:
        """Handle increment seed mode."""
        if last_seed == 0:
            return seed
        return (last_seed + 1) % (2**32)
    
    def handle_decrement_seed(seed: int, last_seed: int = 0, **kwargs) -> int:
        """Handle decrement seed mode."""
        if last_seed == 0:
            return seed
        return (last_seed - 1) % (2**32)
    
    return {
        "fixed": handle_fixed_seed,
        "random": handle_random_seed,
        "increment": handle_increment_seed,
        "decrement": handle_decrement_seed,
    }


def process_seed(seed: int, seed_mode: str, last_seed: int = 0) -> Tuple[int, int]:
    """
    Process seed based on mode and return new seed and last_seed.
    
    Args:
        seed: Input seed value
        seed_mode: Seed mode (fixed, random, increment, decrement)
        last_seed: Previous seed value
        
    Returns:
        Tuple of (new_seed, last_seed_to_store)
    """
    seed_manager = create_seed_manager()
    handler = seed_manager.get(seed_mode, seed_manager["fixed"])
    
    new_seed = handler(seed, last_seed=last_seed)
    
    # Set random seed for reproducibility
    random.seed(new_seed)
    
    return new_seed, new_seed
