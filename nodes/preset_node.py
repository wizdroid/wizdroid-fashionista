from pathlib import Path
import secrets
import random

from ..utils.data_loader import (
    discover_genders,
    load_presets,
)
from ..utils.common import apply_preset, extract_outfit_template, apply_outfit_template

# Constants
PRESET_CATEGORY = "Wizdroid/Outfits/Presets"
NODE_CACHE = {}

def create_preset_node(gender: str):
    base_dir = Path(__file__).resolve().parents[1]
    data_dir = base_dir / "data"
    presets_all = load_presets(data_dir)
    gender_presets = sorted(list(presets_all.get(gender, {}).keys())) if isinstance(presets_all, dict) else []
    preset_options = ["none", "random"] + gender_presets

    class PresetNode:
        _last_seed = 0

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "preset": (preset_options, {"default": "none", "tooltip": "Choose a preset to auto-fill fields. Use 'random' to randomly select from all cultural and themed presets!"}),
                    "preset_colors": ("BOOLEAN", {"default": True, "tooltip": "If OFF, preset fills only clothing types without colors (AI picks colors). If ON, uses preset colors exactly."}),
                    "style_seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1, "tooltip": "Seed for preset randomization. Use 0 to follow main seed, or set different value for consistent random selection."}),
                    "export_preset": ("BOOLEAN", {"default": False, "tooltip": "Export the current preset configuration as JSON"}),
                },
                "optional": {
                    "inputs_json": ("STRING", {"multiline": True, "tooltip": "JSON input to override preset values"}),
                },
            }

        RETURN_TYPES = ("STRING", "STRING", "STRING")
        RETURN_NAMES = ("preset_name", "preset_data", "metadata")
        FUNCTION = "process"
        CATEGORY = PRESET_CATEGORY

        def process(self, preset, preset_colors, style_seed, export_preset, inputs_json=None):
            # Handle random preset selection
            selected_preset = preset
            if selected_preset == "random":
                available_presets = list(presets_all.get(gender, {}).keys())
                if available_presets:
                    # Use style_seed for randomization
                    preset_seed = int(style_seed) if style_seed > 0 else secrets.randbelow(2**32)
                    random.seed(preset_seed)
                    selected_preset = random.choice(available_presets)
                    print(f"[PresetNode] Randomly selected: '{selected_preset}' (seed: {preset_seed})")
                else:
                    selected_preset = "none"

            # Get preset data
            preset_data = {}
            if selected_preset != "none":
                preset_data = presets_all.get(gender, {}).get(selected_preset, {})

            # Apply JSON overrides if provided
            if inputs_json and isinstance(inputs_json, str) and inputs_json.strip():
                try:
                    import json as _json
                    override_data = _json.loads(inputs_json)
                    if isinstance(override_data, dict):
                        preset_data.update(override_data)
                except Exception as e:
                    print(f"[PresetNode] JSON override failed: {e}")

            # Convert to JSON string
            try:
                import json as _json
                preset_json = _json.dumps(preset_data, ensure_ascii=False, indent=2)
            except Exception:
                preset_json = "{}"

            # Create metadata
            metadata = {
                "gender": gender,
                "preset_name": selected_preset,
                "preset_colors": preset_colors,
                "style_seed": style_seed,
                "exported": export_preset,
                "has_data": bool(preset_data),
            }

            try:
                import json as _json
                metadata_json = _json.dumps(metadata, ensure_ascii=False)
            except Exception:
                metadata_json = "{}"

            return (selected_preset, preset_json, metadata_json)

    class_name = f"{gender.capitalize()}PresetNode"
    PresetNode.__name__ = class_name
    return PresetNode, class_name


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

base_dir = Path(__file__).resolve().parents[1]
outfit_data_dir = base_dir / "data" / "outfit"
genders = discover_genders(outfit_data_dir)
for gender in genders:
    Node, name = create_preset_node(gender)
    NODE_CLASS_MAPPINGS[name] = Node
    emoji = "♀️" if gender == "female" else "♂️"
    NODE_DISPLAY_NAME_MAPPINGS[name] = f"{emoji} {gender.capitalize()} Preset"