from pathlib import Path
import secrets

from ..utils.data_loader import (
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
from ..utils.prompt_builder import PromptBuilder
from ..utils.common import apply_preset, extract_outfit_template, apply_outfit_template

# Constants
OUTFIT_CATEGORY = "Wizdroid/Outfits"
NODE_CACHE = {}

def create_outfit_node(gender: str):
    base_dir = Path(__file__).resolve().parents[1]
    data_dir = base_dir / "data"
    gender_data_dir = data_dir / "outfit" / gender

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
    preset_options = ["none", "random"] + gender_presets

    class DynamicOutfitNode:
        _last_seed = 0

        @classmethod
        def INPUT_TYPES(cls):
            inputs = {
                "required": {
                    "preset": (preset_options, {"default": "none", "tooltip": "Choose a preset to auto-fill fields. Use 'random' to randomly select from all cultural and themed presets!"}),
                    "preset_colors": ("BOOLEAN", {"default": True, "tooltip": "If OFF, preset fills only clothing types without colors (AI picks colors). If ON, uses preset colors exactly."}),
                    "avoid_terms": ("STRING", {"default": "", "multiline": True, "placeholder": "Things to exclude (e.g., blurry, low-res, extra fingers)"}),
                    "age_group": (age_groups_options, {"default": "random"}),
                    "character_name": ("STRING", {"default": "", "multiline": False}),
                    "body_type": (body_types_options, {"default": "random"}),
                    "pose": (poses_options, {"default": "random"}),
                    "background": (backgrounds_options, {"default": "random"}),
                    "race": (races_options, {"default": "random"}),
                    "mood": (scene_highlights.get("moods", ["none", "random"]), {"default": "random"}),
                    "time_of_day": (scene_highlights.get("times", ["none", "random"]), {"default": "random"}),
                    "weather": (scene_highlights.get("weather", ["none", "random"]), {"default": "random"}),
                    "color_scheme": (scene_highlights.get("color_schemes", ["none", "random"]), {"default": "random"}),
                    "description_style": (description_styles, {"default": "random"}),
                    "creative_scale": (scale_options, {"default": "none"}),
                    "custom_attributes": ("STRING", {"default": "", "multiline": True, "placeholder": "Enter additional attributes..."}),
                    "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1, "tooltip": "Main seed for image generation. Controls final image output."}),
                    "style_seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1, "tooltip": "Separate seed for outfit/style randomization. Use 0 to follow main seed, or set different value to vary outfit while keeping same image seed."}),
                    "seed_mode": (["fixed", "random", "increment", "decrement"], {"default": "random", "tooltip": "How the main seed behaves: fixed=use exact value, random=new each time, increment/decrement=step from last value"}),
                    "export_preset": ("BOOLEAN", {"default": False}),
                    "lock_preset_fields": ("BOOLEAN", {"default": False, "tooltip": "If on, also lock non-attire style fields (pose, background, etc.) to preset values"}),
                    "enable_cache": ("BOOLEAN", {"default": True, "tooltip": "Cache outputs for identical inputs (faster repeats)"}),
                },
                "hidden": {
                    "makeup_data": ("STRING", {"default": "", "multiline": False}),
                    "_last_seed": ("INT", {"default": 0}),
                    "inputs_json": ("STRING", {"default": "", "multiline": True}),
                },
            }

            for part in body_parts:
                if part != "makeup":
                    inputs["required"][part] = (attire_options.get(part, ["none", "random"]), {"default": "random"})
            return inputs

        RETURN_TYPES = ("STRING", "INT", "STRING", "STRING")
        RETURN_NAMES = ("positive_prompt", "seed", "negative_prompt", "metadata")
        FUNCTION = "process"
        CATEGORY = f"{OUTFIT_CATEGORY}/{gender.capitalize()}"

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
                    print(f"[OutfitNode] Cache key generation failed: {e}")
                    cache_enabled = False

            all_options = {
                "age_group": age_groups_options,
                "race": races_options,
                "body_type": body_types_options,
                "pose": poses_options,
                "background": backgrounds_options,
                "mood": scene_highlights.get("moods", ["none", "random"]),
                "time_of_day": scene_highlights.get("times", ["none", "random"]),
                "weather": scene_highlights.get("weather", ["none", "random"]),
                "color_scheme": scene_highlights.get("color_schemes", ["none", "random"]),
                "description_style": description_styles,
                "creative_scale": scale_options,
                **attire_options,
            }

            allowed_non_attire = {"makeup_data", "pose", "background", "age_group", "race", "body_type", "mood", "time_of_day", "weather", "color_scheme", "description_style", "creative_scale", "character_name", "custom_attributes", "seed", "seed_mode"}
            allowed_keys = set(all_options.keys()) | set(body_parts) | allowed_non_attire

            # Merge JSON inputs prior to preset application
            try:
                import json as _json
                incoming_json = kwargs.get("inputs_json", "") or ""
                if isinstance(incoming_json, str) and incoming_json.strip():
                    incoming_map = _json.loads(incoming_json)
                    if isinstance(incoming_map, dict):
                        for k, v in incoming_map.items():
                            if k in allowed_keys:
                                kwargs[k] = v
            except Exception as _e:
                print(f"[OutfitNode] inputs_json parse ignored: {_e}")

            # Apply preset if selected
            selected_preset = kwargs.get("preset", "none")
            use_preset_colors = bool(kwargs.get("preset_colors", True))
            
            if selected_preset and selected_preset not in ("none", ""):
                # Handle random preset selection
                if selected_preset == "random":
                    available_presets = list(presets_all.get(gender, {}).keys())
                    if available_presets:
                        import random
                        # Use style_seed if provided, otherwise use main seed for randomization
                        preset_seed = int(kwargs.get("style_seed", 0)) or int(use_seed)
                        random.seed(preset_seed)
                        selected_preset = random.choice(available_presets)
                        print(f"[Preset] Randomly selected: '{selected_preset}' (seed: {preset_seed})")
                    else:
                        selected_preset = "none"
                
                if selected_preset != "none":
                    preset_map = presets_all.get(gender, {}).get(selected_preset, {})
                    if isinstance(preset_map, dict):
                        unknown = [k for k in preset_map.keys() if k not in allowed_keys]
                        if unknown:
                            print(f"[Preset] '{selected_preset}' contains unknown keys: {unknown}")
                        
                        if use_preset_colors:
                            # Traditional preset behavior: use exact preset values including colors
                            masked = dict(kwargs)
                            lock_all = bool(kwargs.get("lock_preset_fields", False))
                            for k in preset_map.keys():
                                if k in allowed_keys:
                                    masked[k] = "random"  # ensures apply_preset picks preset value
                            # If strict lock is enabled, mask common non-attire style fields too
                            if lock_all:
                                for extra in ("pose", "background", "mood", "time_of_day", "weather", "color_scheme"):
                                    if extra in preset_map and extra in allowed_keys:
                                        masked[extra] = "random"
                            kwargs = apply_preset(masked, preset_map)
                            print(f"[Preset] Applied '{selected_preset}' with colors")
                        else:
                            # Outfit template behavior: extract clothing without colors
                            outfit_template = extract_outfit_template(preset_map)
                            if outfit_template:
                                kwargs = apply_outfit_template(kwargs, outfit_template)
                                print(f"[Preset] Applied '{selected_preset}' template (no colors) with items: {list(outfit_template.keys())}")

            style_seed = int(kwargs.get("style_seed", 0)) or int(use_seed)
            builder = PromptBuilder(seed=style_seed, data=kwargs, options=all_options)
            final_prompt = builder.build(body_parts=body_parts)
            neg_prompt = builder.get_negative_prompt()
            try:
                import json as _json
                metadata = builder.get_metadata()
                metadata["image_seed"] = use_seed
                metadata["style_seed"] = style_seed
                metadata_json = _json.dumps(metadata, ensure_ascii=False)
            except Exception:
                metadata_json = "{}"

            result = (final_prompt, use_seed, neg_prompt, metadata_json)
            if cache_enabled and cache_key:
                NODE_CACHE[cache_key] = result
            return result

    class_name = f"{gender.capitalize()}OutfitNode"
    DynamicOutfitNode.__name__ = class_name
    return DynamicOutfitNode, class_name


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

base_dir = Path(__file__).resolve().parents[1]
outfit_data_dir = base_dir / "data" / "outfit"
genders = discover_genders(outfit_data_dir)
for gender in genders:
    Node, name = create_outfit_node(gender)
    NODE_CLASS_MAPPINGS[name] = Node
    emoji = "♀️" if gender == "female" else "♂️"
    NODE_DISPLAY_NAME_MAPPINGS[name] = f"{emoji} {gender.capitalize()} Outfit"
