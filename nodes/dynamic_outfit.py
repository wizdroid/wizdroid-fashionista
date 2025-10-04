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
)
from ..utils.prompt_builder import PromptBuilder

# Constants
OUTFIT_CATEGORY = "Wizdroid/Outfits/Dynamic"
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

    class DynamicOutfitNode:
        _last_seed = 0

        @classmethod
        def INPUT_TYPES(cls):
            inputs = {
                "required": {
                    "avoid_terms": ("STRING", {"default": "", "multiline": True, "placeholder": "Things to exclude (e.g., blurry, low-res, extra fingers)"}),
                    "randomize_all": ("BOOLEAN", {"default": False, "tooltip": "Randomize all fields that are set to 'random'"}),
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
                    "seed_mode": (["fixed", "random"], {"default": "random", "tooltip": "How the main seed behaves: fixed=use exact value, random=new each time"}),
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
        CATEGORY = OUTFIT_CATEGORY

        def process(self, **kwargs):
            seed = int(kwargs.get("seed", 0))
            seed_mode = kwargs.get("seed_mode", "random")

            if seed_mode == "fixed":
                use_seed = seed
            else:  # random
                use_seed = secrets.randbelow(2**32)

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

            allowed_non_attire = {"makeup_data", "pose", "background", "age_group", "race", "body_type", "mood", "time_of_day", "weather", "color_scheme", "description_style", "creative_scale", "character_name", "custom_attributes", "seed", "seed_mode", "randomize_all"}
            allowed_keys = set(all_options.keys()) | set(body_parts) | allowed_non_attire

            # Merge JSON inputs if provided
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

            # Handle randomize_all option
            randomize_all = bool(kwargs.get("randomize_all", False))
            if randomize_all:
                for key in all_options.keys():
                    if kwargs.get(key) == "random" or kwargs.get(key) is None:
                        kwargs[key] = "random"

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
