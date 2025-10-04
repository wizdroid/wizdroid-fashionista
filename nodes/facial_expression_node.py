"""
Facial Expression & Lighting Node for ComfyUI.
Generates prompts with specific facial angles, lighting, expressions, and integrates with outfit presets.
"""

import json
import random
import secrets
from pathlib import Path
from typing import Dict, List, Tuple, Any

from ..utils.data_loader import (
    load_gender_presets,
    load_global_options,
    load_scene_highlights,
    load_description_styles,
)

# Facial expression and angle options
FACIAL_EXPRESSIONS = [
    "none", "random",
    "smiling", "laughing", "grinning", "beaming",
    "serious", "contemplative", "focused", "determined",
    "mysterious", "sultry", "seductive", "alluring",
    "surprised", "shocked", "amazed", "curious",
    "sad", "melancholic", "wistful", "pensive",
    "angry", "fierce", "intense", "stern",
    "peaceful", "serene", "calm", "relaxed",
    "playful", "mischievous", "cheeky", "flirty",
    "confident", "proud", "regal", "commanding",
    "shy", "bashful", "coy", "demure",
    "excited", "enthusiastic", "joyful", "ecstatic"
]

FACIAL_ANGLES = [
    "none", "random",
    "front view", "straight on", "direct gaze",
    "three-quarter view", "3/4 angle", "slight turn",
    "profile view", "side profile", "silhouette",
    "looking over shoulder", "back turned", "glancing back",
    "looking up", "upward gaze", "chin raised",
    "looking down", "downward gaze", "eyes cast down",
    "tilted head", "head cocked", "sideways glance",
    "close-up face", "portrait shot", "headshot",
    "from above", "bird's eye view", "looking down at subject",
    "from below", "low angle", "looking up at subject"
]

LIGHTING_STYLES = [
    "none", "random",
    "natural daylight", "soft natural light", "golden hour",
    "dramatic lighting", "high contrast", "chiaroscuro",
    "soft diffused light", "studio lighting", "professional lighting",
    "rim lighting", "backlighting", "edge lighting",
    "side lighting", "split lighting", "Rembrandt lighting",
    "butterfly lighting", "clamshell lighting", "broad lighting",
    "candlelight", "warm amber light", "firelight",
    "neon lighting", "colorful lighting", "moody lighting",
    "harsh shadows", "deep shadows", "mysterious shadows",
    "bright even lighting", "flat lighting", "overcast light",
    "sunset lighting", "magic hour", "blue hour",
    "moonlight", "silvery light", "cool blue light"
]

MOOD_ENHANCERS = [
    "none", "random",
    "intimate atmosphere", "romantic mood", "passionate energy",
    "mysterious ambiance", "dramatic tension", "cinematic feel",
    "ethereal quality", "dreamy atmosphere", "fantasy mood",
    "edgy vibe", "rebellious energy", "urban grit",
    "elegant sophistication", "refined atmosphere", "luxury feel",
    "playful energy", "youthful spirit", "carefree mood",
    "powerful presence", "commanding aura", "confident energy",
    "serene tranquility", "peaceful calm", "zen atmosphere"
]

COMPOSITION_STYLES = [
    "none", "random",
    "rule of thirds", "centered composition", "symmetrical",
    "close crop", "medium shot", "wide shot",
    "tight framing", "breathing room", "negative space",
    "diagonal composition", "leading lines", "frame within frame",
    "shallow depth of field", "bokeh background", "sharp focus",
    "environmental portrait", "contextual background", "isolated subject"
]


class FacialExpressionNode:
    """Node for generating facial expression and lighting prompts with preset integration."""
    
    _last_seed = 0
    
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parents[1]
        self.data_dir = self.base_dir / "data"
        
    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for the ComfyUI node interface."""
        # Load preset options
        base_dir = Path(__file__).resolve().parents[1]
        data_dir = base_dir / "data"
        
        # Load presets for both genders
        female_presets = load_gender_presets(data_dir / "outfit" / "female")
        male_presets = load_gender_presets(data_dir / "outfit" / "male")
        
        # Combine all preset names
        all_presets = set()
        all_presets.update(female_presets.keys())
        all_presets.update(male_presets.keys())
        preset_options = ["none", "random"] + sorted(list(all_presets))
        
        # Load other options
        backgrounds_options = load_global_options(data_dir, "backgrounds.json", "backgrounds")
        age_groups_options = load_global_options(data_dir, "age_groups.json", "age_groups")
        scene_highlights = load_scene_highlights(data_dir / "styles")
        description_styles = load_description_styles(data_dir / "styles")
        
        return {
            "required": {
                "gender": (["female", "male"], {"default": "female"}),
                "facial_expression": (FACIAL_EXPRESSIONS, {"default": "random"}),
                "facial_angle": (FACIAL_ANGLES, {"default": "random"}),
                "lighting_style": (LIGHTING_STYLES, {"default": "random"}),
                "mood_enhancer": (MOOD_ENHANCERS, {"default": "random"}),
                "composition": (COMPOSITION_STYLES, {"default": "random"}),
                "outfit_preset": (preset_options, {"default": "none"}),
                "background": (backgrounds_options, {"default": "random"}),
                "age_group": (age_groups_options, {"default": "random"}),
                "time_of_day": (scene_highlights.get("times", ["none", "random"]), {"default": "random"}),
                "color_scheme": (scene_highlights.get("color_schemes", ["none", "random"]), {"default": "random"}),
                "description_style": (description_styles, {"default": "random"}),
                "custom_additions": ("STRING", {"default": "", "multiline": True, "placeholder": "Additional custom details..."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1}),
                "randomize_all": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "character_description": ("STRING", {"default": "", "multiline": True, "placeholder": "Base character description..."}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("formatted_prompt", "metadata", "debug_info")
    FUNCTION = "generate_facial_prompt"
    CATEGORY = "Wizdroid/Outfits/Expression"
    
    def generate_facial_prompt(
        self,
        gender: str = "female",
        facial_expression: str = "random",
        facial_angle: str = "random",
        lighting_style: str = "random",
        mood_enhancer: str = "random",
        composition: str = "random",
        outfit_preset: str = "none",
        background: str = "random",
        age_group: str = "random",
        time_of_day: str = "random",
        color_scheme: str = "random",
        description_style: str = "random",
        custom_additions: str = "",
        seed: int = 0,
        randomize_all: bool = True,
        character_description: str = "",
        **kwargs
    ) -> Tuple[str, str, str]:
        """Generate a formatted prompt with facial expressions, angles, and lighting."""
        
        # Set random seed
        use_seed = seed if seed > 0 else secrets.randbelow(2**32)
        random.seed(use_seed)
        
        # Load gender-specific presets
        gender_presets = load_gender_presets(self.data_dir / "outfit" / gender)
        
        # Handle outfit preset selection
        selected_preset = {}
        preset_name = "none"
        if outfit_preset and outfit_preset not in ("none", ""):
            if outfit_preset == "random":
                available_presets = list(gender_presets.keys())
                if available_presets:
                    preset_name = random.choice(available_presets)
                    selected_preset = gender_presets.get(preset_name, {})
            elif outfit_preset in gender_presets:
                preset_name = outfit_preset
                selected_preset = gender_presets.get(outfit_preset, {})
        
        # Randomize selections if enabled
        if randomize_all:
            facial_expression = self._random_choice_if_random(facial_expression, FACIAL_EXPRESSIONS)
            facial_angle = self._random_choice_if_random(facial_angle, FACIAL_ANGLES)
            lighting_style = self._random_choice_if_random(lighting_style, LIGHTING_STYLES)
            mood_enhancer = self._random_choice_if_random(mood_enhancer, MOOD_ENHANCERS)
            composition = self._random_choice_if_random(composition, COMPOSITION_STYLES)
            
            # Randomize other options
            if background == "random":
                backgrounds = load_global_options(self.data_dir, "backgrounds.json", "backgrounds")
                background = random.choice([b for b in backgrounds if b not in ("none", "random")])
            
            if age_group == "random":
                ages = load_global_options(self.data_dir, "age_groups.json", "age_groups")
                age_group = random.choice([a for a in ages if a not in ("none", "random")])
                
            if time_of_day == "random":
                times = load_scene_highlights(self.data_dir / "styles").get("times", [])
                time_of_day = random.choice([t for t in times if t not in ("none", "random")])
                
            if color_scheme == "random":
                colors = load_scene_highlights(self.data_dir / "styles").get("color_schemes", [])
                color_scheme = random.choice([c for c in colors if c not in ("none", "random")])
        
        # Build prompt components
        prompt_parts = []
        
        # Start with character description if provided
        if character_description.strip():
            prompt_parts.append(character_description.strip())
        
        # Add age group
        if age_group and age_group != "none":
            prompt_parts.append(f"{age_group} {gender}")
        else:
            prompt_parts.append(gender)
        
        # Add outfit from preset if available
        outfit_parts = []
        if selected_preset:
            for part in ["torso", "legs", "feet", "headgear", "neck", "ear", "fingers", "hand", "waist"]:
                if part in selected_preset:
                    outfit_parts.append(selected_preset[part])
        
        if outfit_parts:
            prompt_parts.append(f"wearing {', '.join(outfit_parts)}")
        
        # Add facial expression
        if facial_expression and facial_expression != "none":
            prompt_parts.append(f"with {facial_expression} expression")
        
        # Add composition and angle
        composition_text = ""
        if composition and composition != "none":
            composition_text = f"{composition}, "
            
        if facial_angle and facial_angle != "none":
            prompt_parts.append(f"{composition_text}{facial_angle}")
        elif composition_text:
            prompt_parts.append(composition_text.rstrip(", "))
        
        # Add lighting
        if lighting_style and lighting_style != "none":
            prompt_parts.append(f"illuminated by {lighting_style}")
        
        # Add background and setting
        setting_parts = []
        if background and background != "none":
            setting_parts.append(f"in {background}")
            
        if time_of_day and time_of_day != "none":
            setting_parts.append(f"during {time_of_day}")
            
        if setting_parts:
            prompt_parts.append(", ".join(setting_parts))
        
        # Add mood enhancer
        if mood_enhancer and mood_enhancer != "none":
            prompt_parts.append(f"with {mood_enhancer}")
        
        # Add color scheme
        if color_scheme and color_scheme != "none":
            prompt_parts.append(f"using {color_scheme}")
        
        # Add custom additions
        if custom_additions.strip():
            prompt_parts.append(custom_additions.strip())
        
        # Join all parts
        base_prompt = ", ".join(prompt_parts)
        
        # Apply description style if specified
        final_prompt = self._apply_description_style(base_prompt, description_style)
        
        # Create metadata
        metadata = {
            "gender": gender,
            "facial_expression": facial_expression,
            "facial_angle": facial_angle,
            "lighting_style": lighting_style,
            "mood_enhancer": mood_enhancer,
            "composition": composition,
            "outfit_preset": preset_name,
            "background": background,
            "age_group": age_group,
            "time_of_day": time_of_day,
            "color_scheme": color_scheme,
            "description_style": description_style,
            "seed": use_seed,
            "randomize_all": randomize_all
        }
        
        # Create debug info
        debug_info = f"Selected: Expression={facial_expression}, Angle={facial_angle}, Lighting={lighting_style}, Preset={preset_name}"
        
        try:
            metadata_json = json.dumps(metadata, ensure_ascii=False)
        except Exception:
            metadata_json = "{}"
        
        return (final_prompt, metadata_json, debug_info)
    
    def _random_choice_if_random(self, value: str, options: List[str]) -> str:
        """Return random choice from options if value is 'random', otherwise return value."""
        if value == "random":
            valid_options = [opt for opt in options if opt not in ("none", "random")]
            return random.choice(valid_options) if valid_options else "none"
        return value
    
    def _apply_description_style(self, prompt: str, style: str) -> str:
        """Apply description style formatting to the prompt."""
        if style == "random":
            styles = load_description_styles(self.data_dir / "styles")
            style = random.choice([s for s in styles if s != "random"])
        
        if style == "none" or not style:
            return prompt
            
        # Apply different formatting based on style
        style_formatters = {
            "photorealistic": f"A highly detailed, photorealistic image of {prompt}",
            "artistic": f"An artistic representation of {prompt}",
            "cinematic": f"A cinematic shot of {prompt}",
            "portrait": f"A professional portrait of {prompt}",
            "fashion": f"A high-fashion photograph of {prompt}",
            "dramatic": f"A dramatically lit scene featuring {prompt}",
            "natural": f"A natural, candid image of {prompt}",
            "studio": f"A studio photograph of {prompt}",
            "editorial": f"An editorial-style image of {prompt}",
            "lifestyle": f"A lifestyle photograph showing {prompt}"
        }
        
        return style_formatters.get(style, prompt)


# Node registration
NODE_CLASS_MAPPINGS = {
    "FacialExpressionNode": FacialExpressionNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FacialExpressionNode": "🎭 Facial Expression & Lighting"
}