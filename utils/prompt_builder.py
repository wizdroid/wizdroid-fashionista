import json
import random
from typing import Any, Dict, List

from .common import safe_random_choice

class PromptBuilder:
    def __init__(self, seed: int, data: Dict[str, Any], options: Dict[str, List[str]]):
        self.seed = seed
        self.data = data
        self.options = options
        self.prompt_parts = []
        random.seed(self.seed)

    def _add_part(self, key: str, label: str, is_random_allowed: bool = True):
        value = self.data.get(key, "none")
        if value == "none":
            return

        if value == "random" and is_random_allowed:
            valid_options = self.options.get(key, [])
            value = safe_random_choice(valid_options)
        
        if value and value != "none":
            self.prompt_parts.append(f"{label}: {value}")

    def _process_attire(self, body_parts: List[str]):
        attire_parts = []
        for part in body_parts:
            if part == "makeup":
                continue

            value = self.data.get(part, "none")
            if value == "random":
                options = self.options.get(part, [])
                selected = safe_random_choice(options)
                if selected != "none":
                    attire_parts.append(f"{part}: {selected}")
            elif value != "none":
                attire_parts.append(f"{part}: {value}")
        
        if attire_parts:
            self.prompt_parts.append("Attire: " + ", ".join(attire_parts))

    def _process_makeup(self):
        makeup_parts = []
        makeup_data = self.data.get("makeup_data", "")
        if not makeup_data:
            return

        try:
            makeup_items = json.loads(makeup_data)
            for item in makeup_items:
                if not item.get("enabled", True) or item.get("type") == "none":
                    continue
                
                makeup_type = item.get("type")
                intensity = item.get("intensity", "medium")
                color = item.get("color", "none")

                if color and color != "none":
                    makeup_parts.append(f"{makeup_type} ({color}, {intensity})")
                else:
                    makeup_parts.append(f"{makeup_type} ({intensity})")
        except (json.JSONDecodeError, TypeError) as e:
            print(f"[OutfitNode] Error parsing makeup data: {e}")

        if makeup_parts:
            self.prompt_parts.append("Makeup: " + ", ".join(makeup_parts))

    def build(self, body_parts: List[str]) -> str:
        character_name = self.data.get("character_name", "").strip()
        if character_name:
            self.prompt_parts.append(f"Character: {character_name}")

        self._add_part("age_group", "Age")
        self._add_part("race", "Race")
        self._add_part("body_type", "Body type")

        self._process_attire(body_parts)
        self._process_makeup()

        self._add_part("pose", "Pose")
        self._add_part("background", "Background")

        # Scene/style controls
        self._add_part("mood", "Mood")
        self._add_part("time_of_day", "Time")
        self._add_part("weather", "Weather")
        self._add_part("color_scheme", "Color scheme")
        # These are selectors; the actual mapping to instruction text can be handled downstream
        self._add_part("description_style", "Style")
        self._add_part("creative_scale", "Scale")

        custom_attributes = self.data.get("custom_attributes", "").strip()
        if custom_attributes:
            self.prompt_parts.append(f"Additional: {custom_attributes}")

        # Negative/avoid terms
        avoid_terms = self.data.get("avoid_terms", "").strip()
        if avoid_terms:
            self.prompt_parts.append(f"Avoid: {avoid_terms}")

        return ", ".join(self.prompt_parts)
