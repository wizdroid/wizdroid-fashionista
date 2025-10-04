from pathlib import Path
import secrets

from ..utils.data_loader import (
    load_gender_presets,
    load_global_options,
    load_scene_highlights,
    load_description_styles,
    load_scale_options,
    load_body_types,
)
from ..utils.prompt_builder import PromptBuilder

# Constants
OUTFIT_CATEGORY = "Wizdroid/Outfits/Presets"
NODE_CACHE = {}


def create_preset_outfit_node(gender: str):
    base_dir = Path(__file__).resolve().parents[1]
    data_dir = base_dir / "data"
    gender_data_dir = data_dir / "outfit" / gender
    gender_presets = load_gender_presets(gender_data_dir)
    preset_options = ["none", "random"] + sorted(list(gender_presets.keys()))

    backgrounds_options = load_global_options(data_dir, "backgrounds.json", "backgrounds")
    age_groups_options = load_global_options(data_dir, "age_groups.json", "age_groups")
    body_types_options = load_body_types(data_dir / "outfit" / gender)
    scene_highlights = load_scene_highlights(data_dir / "styles")
    description_styles = load_description_styles(data_dir / "styles")
    scale_options = load_scale_options(data_dir / "styles")

    class PresetOutfitNode:
        _last_seed = 0

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "preset": (preset_options, {"default": "none", "tooltip": "Choose a preset outfit. Select 'random' for a surprise!"}),
                    "age_group": (age_groups_options, {"default": "random", "tooltip": "Age group for the character"}),
                    "character_name": ("STRING", {"default": "", "multiline": False, "placeholder": "Character name (optional)"}),
                    "body_type": (body_types_options, {"default": "random", "tooltip": "Body type for the character"}),
                    "background": (backgrounds_options, {"default": "random"}),
                    "mood": (scene_highlights.get("moods", ["none", "random"]), {"default": "random"}),
                    "time_of_day": (scene_highlights.get("times", ["none", "random"]), {"default": "random"}),
                    "weather": (scene_highlights.get("weather", ["none", "random"]), {"default": "random"}),
                    "color_scheme": (scene_highlights.get("color_schemes", ["none", "random"]), {"default": "random"}),
                    "description_style": (description_styles, {"default": "random"}),
                    "creative_scale": (scale_options, {"default": "none"}),
                    "custom_attributes": ("STRING", {"default": "", "multiline": True, "placeholder": "Additional attributes..."}),
                    "additional_custom_input": ("STRING", {"default": "", "multiline": True, "placeholder": "Extra custom details, personality traits, etc."}),
                    "avoid_terms": ("STRING", {"default": "", "multiline": True, "placeholder": "Things to exclude"}),
                    "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1, "tooltip": "Main seed for image generation"}),
                    "style_seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1, "tooltip": "Separate seed for style randomization"}),
                    "seed_mode": (["fixed", "random", "increment", "decrement"], {"default": "random"}),
                    "enable_cache": ("BOOLEAN", {"default": True}),
                },
                "hidden": {
                    "_last_seed": ("INT", {"default": 0}),
                },
            }

        RETURN_TYPES = ("STRING", "INT", "STRING", "STRING")
        RETURN_NAMES = ("positive_prompt", "seed", "negative_prompt", "metadata")
        FUNCTION = "process"
        CATEGORY = OUTFIT_CATEGORY

        def process(self, **kwargs):
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

            # Cache key generation
            cache_enabled = bool(kwargs.get("enable_cache", True))
            cache_key = None
            if cache_enabled:
                try:
                    import json as _json
                    sig_map = {k: kwargs.get(k) for k in sorted(self.INPUT_TYPES()["required"].keys())}
                    sig_map["_gender"] = gender
                    sig_map["_style_seed"] = int(kwargs.get("style_seed", 0)) or 0
                    sig = _json.dumps(sig_map, sort_keys=True, ensure_ascii=False)
                    cache_key = (sig, seed_mode, use_seed)
                    if cache_key in NODE_CACHE:
                        return NODE_CACHE[cache_key]
                except Exception as e:
                    print(f"[PresetOutfitNode] Cache key generation failed: {e}")
                    cache_enabled = False

            # Get selected preset
            selected_preset = kwargs.get("preset", "none")

            if selected_preset and selected_preset not in ("none", ""):
                if selected_preset == "random":
                    # Random selection from gender-specific presets only
                    available_presets = list(gender_presets.keys())
                    if available_presets:
                        import random
                        preset_seed = int(kwargs.get("style_seed", 0)) or int(use_seed)
                        random.seed(preset_seed)
                        selected_preset = random.choice(available_presets)
                        print(f"[Preset] Randomly selected '{selected_preset}' for {gender} (seed: {preset_seed})")
                    else:
                        selected_preset = "none"

                if selected_preset != "none":
                    preset_map = gender_presets.get(selected_preset, {})
                    if isinstance(preset_map, dict):
                        # Apply preset values
                        allowed_keys = {
                            "background", "pose", "mood", "time_of_day", "weather", "color_scheme",
                            "description_style", "creative_scale", "character_name", "custom_attributes",
                            "age_group", "race", "body_type", "makeup_data", "additional_custom_input"
                        }

                        # Apply preset values to kwargs
                        for k, v in preset_map.items():
                            if k in allowed_keys:
                                kwargs[k] = v

                        print(f"[Preset] Applied '{selected_preset}' for {gender}")

            # Build the prompt using PromptBuilder
            style_seed = int(kwargs.get("style_seed", 0)) or int(use_seed)

            # Create a minimal body_parts dict for the builder
            body_parts = ["torso", "legs", "feet", "headgear", "neck", "ear", "fingers", "hand", "waist"]

            # Load options for the builder
            backgrounds_options = load_global_options(data_dir, "backgrounds.json", "backgrounds")
            age_groups_options = load_global_options(data_dir, "age_groups.json", "age_groups")
            body_types_options = load_body_types(data_dir / "outfit" / gender)
            scene_highlights = load_scene_highlights(data_dir / "styles")
            description_styles = load_description_styles(data_dir / "styles")
            scale_options = load_scale_options(data_dir / "styles")

            all_options = {
                "background": backgrounds_options,
                "age_group": age_groups_options,
                "body_type": body_types_options,
                "mood": scene_highlights.get("moods", ["none", "random"]),
                "time_of_day": scene_highlights.get("times", ["none", "random"]),
                "weather": scene_highlights.get("weather", ["none", "random"]),
                "color_scheme": scene_highlights.get("color_schemes", ["none", "random"]),
                "description_style": description_styles,
                "creative_scale": scale_options,
            }

            builder = PromptBuilder(seed=style_seed, data=kwargs, options=all_options)
            final_prompt = builder.build(body_parts=body_parts)
            neg_prompt = builder.get_negative_prompt()

            try:
                import json as _json
                metadata = builder.get_metadata()
                metadata["image_seed"] = use_seed
                metadata["style_seed"] = style_seed
                metadata["selected_preset"] = selected_preset
                metadata["gender"] = gender
                metadata_json = _json.dumps(metadata, ensure_ascii=False)
            except Exception:
                metadata_json = "{}"

            result = (final_prompt, use_seed, neg_prompt, metadata_json)
            if cache_enabled and cache_key:
                NODE_CACHE[cache_key] = result
            return result

    class_name = f"{gender.capitalize()}PresetOutfitNode"
    PresetOutfitNode.__name__ = class_name
    return PresetOutfitNode, class_name


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

base_dir = Path(__file__).resolve().parents[1]
outfit_data_dir = base_dir / "data" / "outfit"
genders = ["female", "male"]  # Only create nodes for genders that have presets

for gender in genders:
    Node, name = create_preset_outfit_node(gender)
    NODE_CLASS_MAPPINGS[name] = Node
    emoji = "♀️" if gender == "female" else "♂️"
    NODE_DISPLAY_NAME_MAPPINGS[name] = f"{emoji} {gender.capitalize()} Preset Outfit"
