import secrets
from pathlib import Path

from .utils.data_loader import (
    discover_genders,
    discover_body_parts,
    load_outfit_data,
    load_global_options,
    load_body_types,
    load_scene_highlights,
    load_description_styles,
    load_scale_options,
    load_presets,
)
from .utils.prompt_builder import PromptBuilder
from .utils.common import apply_preset


def create_outfit_node(gender: str):
    """Factory function to create a customized DynamicOutfitNode class for a specific gender."""
    
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    gender_data_dir = data_dir / "outfit" / gender

    # Discover and load data using utility functions
    body_parts = discover_body_parts(gender_data_dir)
    attire_options = load_outfit_data(gender_data_dir, body_parts)
    
    poses_options = load_global_options(gender_data_dir, "poses.json", "poses")
    backgrounds_options = load_global_options(data_dir, "backgrounds.json", "backgrounds")
    races_options = load_global_options(data_dir, "race.json", "races")
    age_groups_options = load_global_options(data_dir, "age_groups.json", "age_groups")
    body_types_options = load_body_types(gender_data_dir)
    styles_dir = data_dir / "styles"
    scene_highlights = load_scene_highlights(styles_dir)
    description_styles = load_description_styles(styles_dir)
    scale_options = load_scale_options(styles_dir)
    presets_all = load_presets(data_dir)
    gender_presets = sorted(list(presets_all.get(gender, {}).keys())) if isinstance(presets_all, dict) else []
    preset_options = ["none"] + gender_presets
    
    class DynamicOutfitNode:
        _last_seed = 0

        @classmethod
        def INPUT_TYPES(cls):
            """Define node inputs based on loaded data."""
            inputs = {
                "required": {
                    "preset": (preset_options, {"default": "none"}),
                    "age_group": (age_groups_options, {"default": "random"}),
                    "character_name": ("STRING", {"default": "", "multiline": False}),
                    "body_type": (body_types_options, {"default": "random"}),
                    "pose": (poses_options, {"default": "random"}),
                    "background": (backgrounds_options, {"default": "random"}),
                    "race": (races_options, {"default": "random"}),
                    # Scene/style controls
                    "mood": (scene_highlights.get("moods", ["none", "random"]), {"default": "random"}),
                    "time_of_day": (scene_highlights.get("times", ["none", "random"]), {"default": "random"}),
                    "weather": (scene_highlights.get("weather", ["none", "random"]), {"default": "random"}),
                    "color_scheme": (scene_highlights.get("color_schemes", ["none", "random"]), {"default": "random"}),
                    "description_style": (description_styles, {"default": "random"}),
                    "creative_scale": (scale_options, {"default": "none"}),
                    "custom_attributes": (
                        "STRING",
                        {
                            "default": "",
                            "multiline": True,
                            "placeholder": "Enter additional attributes...",
                        },
                    ),
                    "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1}),
                    "seed_mode": (
                        ["fixed", "random", "increment", "decrement"],
                        {"default": "random"},
                    ),
                },
                "hidden": {
                    "makeup_data": ("STRING", {"default": "", "multiline": False}),
                    "_last_seed": ("INT", {"default": 0}),
                },
            }

            # Add attire inputs dynamically
            for part in body_parts:
                if part != "makeup":
                    inputs["required"][part] = (attire_options.get(part, ["none", "random"]), {"default": "random"})
            
            return inputs

        RETURN_TYPES = ("STRING", "INT")
        FUNCTION = "process"
        CATEGORY = f"👗 Outfit/{gender.capitalize()}"

        def process(self, **kwargs):
            """Process inputs and build the prompt."""
            seed = int(kwargs.get("seed", 0))
            seed_mode = kwargs.get("seed_mode", "random")
            last_seed = int(kwargs.get("_last_seed", 0))

            if seed_mode == "fixed":
                use_seed = seed
            elif seed_mode == "random":
                use_seed = secrets.randbelow(2**32)
            elif seed_mode == "increment":
                use_seed = (last_seed + 1) % (2**32) if last_seed != 0 else seed
            elif seed_mode == "decrement":
                use_seed = (last_seed - 1) % (2**32) if last_seed != 0 else seed
            else:
                use_seed = seed
            
            print(f"[{self.__class__.__name__}] Using seed: {use_seed} (mode: {seed_mode})")

            # Apply preset if selected (fills only empty/none/random fields)
            selected_preset = kwargs.get("preset", "none")
            if selected_preset and selected_preset != "none":
                preset_map = presets_all.get(gender, {}).get(selected_preset, {})
                if isinstance(preset_map, dict):
                    kwargs = apply_preset(kwargs, preset_map)

            # Consolidate all options for the prompt builder
            all_options = {
                "age_group": age_groups_options,
                "race": races_options,
                "body_type": body_types_options,
                "pose": poses_options,
                "background": backgrounds_options,
                # scene/style
                "mood": scene_highlights.get("moods", ["none", "random"]),
                "time_of_day": scene_highlights.get("times", ["none", "random"]),
                "weather": scene_highlights.get("weather", ["none", "random"]),
                "color_scheme": scene_highlights.get("color_schemes", ["none", "random"]),
                "description_style": description_styles,
                "creative_scale": scale_options,
                **attire_options,
            }

            builder = PromptBuilder(seed=use_seed, data=kwargs, options=all_options)
            final_prompt = builder.build(body_parts=body_parts)
            
            return (final_prompt, use_seed)

    # Set a dynamic name for the class
    class_name = f"{gender.capitalize()}OutfitNode"
    DynamicOutfitNode.__name__ = class_name
    
    return DynamicOutfitNode, class_name


# Node registration
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Discover genders and create nodes for each
base_dir = Path(__file__).parent
outfit_data_dir = base_dir / "data" / "outfit"
genders = discover_genders(outfit_data_dir)

for gender in genders:
    Node, name = create_outfit_node(gender)
    NODE_CLASS_MAPPINGS[name] = Node
    
    # Set display name with emoji
    emoji = "♀️" if gender == "female" else "♂️"
    NODE_DISPLAY_NAME_MAPPINGS[name] = f"{emoji} {gender.capitalize()} Outfit"