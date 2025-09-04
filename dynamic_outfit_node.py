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
        _cache = {}

        @classmethod
        def INPUT_TYPES(cls):
            """Define node inputs based on loaded data."""
            inputs = {
                "required": {
                    "preset": (
                        preset_options,
                        {
                            "default": "none",
                            "tooltip": "Choose a preset to auto-fill empty fields (none/random)",
                        },
                    ),
                    "avoid_terms": (
                        "STRING",
                        {
                            "default": "",
                            "multiline": True,
                            "placeholder": "Things to exclude (e.g., blurry, low-res, extra fingers)",
                        },
                    ),
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
                    "style_seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1, "tooltip": "Seed used to randomize outfit/style choices. 0 = follow image seed."}),
                    "seed_mode": (
                        ["fixed", "random", "increment", "decrement"],
                        {"default": "random"},
                    ),
                    "export_preset": ("BOOLEAN", {"default": False}),
                    "enable_cache": ("BOOLEAN", {"default": True, "tooltip": "Cache outputs for identical inputs (faster repeats)"}),
                },
                "hidden": {
                    "makeup_data": ("STRING", {"default": "", "multiline": False}),
                    "_last_seed": ("INT", {"default": 0}),
                    "inputs_json": ("STRING", {"default": "", "multiline": True}),
                },
            }

            # Add attire inputs dynamically
            for part in body_parts:
                if part != "makeup":
                    inputs["required"][part] = (attire_options.get(part, ["none", "random"]), {"default": "random"})
            
            return inputs

        # Outputs:
        # 0: positive prompt (STRING)
        # 1: seed (INT)
        # 2: negative prompt (STRING)
        # 3: metadata JSON (STRING)
        RETURN_TYPES = ("STRING", "INT", "STRING", "STRING")
        FUNCTION = "process"
        CATEGORY = f"Wizdroid/Outfits/{gender.capitalize()}"

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

            # Consolidate all options for the prompt builder (also used for preset validation)
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

            allowed_non_attire = {"makeup_data", "pose", "background", "age_group", "race", "body_type", "mood", "time_of_day", "weather", "color_scheme", "description_style", "creative_scale", "character_name", "custom_attributes", "seed", "seed_mode"}
            allowed_keys = set(all_options.keys()) | set(body_parts) | allowed_non_attire

            # Merge JSON inputs (from helper/applier) before applying preset
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

            # Optional cache key (after JSON merge but before randoms)
            try:
                import json as _json
                cache_enabled = bool(kwargs.get("enable_cache", True))
                if cache_enabled:
                    # Build a stable signature using allowed keys only
                    sig_map = {k: kwargs.get(k) for k in sorted(allowed_keys)}
                    sig_map["_gender"] = gender
                    sig_map["_body_parts"] = body_parts
                    sig_map["_style_seed"] = int(kwargs.get("style_seed", 0)) or 0
                    sig = _json.dumps(sig_map, sort_keys=True, ensure_ascii=False)
                    cache_key = (sig, seed_mode, use_seed)
                    if cache_key in self._cache:
                        cached = self._cache[cache_key]
                        return cached
            except Exception:
                cache_enabled = False

            # Apply preset if selected (fills only empty/none/random fields)
            selected_preset = kwargs.get("preset", "none")
            if selected_preset and selected_preset != "none":
                preset_map = presets_all.get(gender, {}).get(selected_preset, {})
                if isinstance(preset_map, dict):
                    # Warn if preset has keys that don't match inputs (for curation)
                    unknown = [k for k in preset_map.keys() if k not in allowed_keys]
                    if unknown:
                        print(f"[Preset] '{selected_preset}' contains unknown keys: {unknown}")
                    kwargs = apply_preset(kwargs, preset_map)

            # Optional export of current selection as a preset snippet
            if kwargs.get("export_preset", False):
                exclude_keys = {"seed", "seed_mode", "_last_seed", "preset", "character_name", "custom_attributes"}
                export_map = {}
                for k, v in kwargs.items():
                    if k in exclude_keys:
                        continue
                    if k not in allowed_keys:
                        continue
                    if isinstance(v, str) and v.strip() in ("", "none", "random"):
                        continue
                    export_map[k] = v
                try:
                    import json
                    snippet = json.dumps(export_map, ensure_ascii=False, indent=2)
                    print(f"[Preset Export][{gender}] Copy this under your preset name in data/presets.json:\n{snippet}")
                except Exception as e:
                    print(f"[Preset Export] Failed to serialize preset: {e}")

            # Style seed: if 0, follow image seed
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
            if cache_enabled:
                try:
                    self._cache[cache_key] = result
                except Exception:
                    pass
            return result

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