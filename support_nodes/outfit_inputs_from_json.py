from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from ..utils.data_loader import (
    discover_genders,
    discover_body_parts,
    load_outfit_data,
    load_global_options,
    load_body_types,
)


def _common_keys(base_dir: Path, gender: str) -> Tuple[List[str], List[str]]:
    data_dir = base_dir / "data"
    gender_dir = data_dir / "outfit" / gender
    parts = discover_body_parts(gender_dir)
    # canonical order for non-attire fields the main node understands
    style_keys = [
        "preset",
        "age_group",
        "race",
        "body_type",
        "pose",
        "background",
        "mood",
        "time_of_day",
        "weather",
        "color_scheme",
        "description_style",
        "creative_scale",
        "character_name",
        "custom_attributes",
        "avoid_terms",
    ]
    # body parts appended after style keys for wiring convenience
    ordered = style_keys + [p for p in parts if p != "makeup"] + ["makeup_data", "inputs_json"]
    return parts, ordered


def create_bridge_node(gender: str):
    base_dir = Path(__file__).resolve().parents[1]
    _parts, ordered_keys = _common_keys(base_dir, gender)

    class OutfitInputsFromJSON:
        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "merged_json": ("STRING", {"default": "", "multiline": True, "placeholder": "Paste merged_json here"}),
                }
            }

        RETURN_TYPES = tuple(["STRING"] * len(ordered_keys))
        RETURN_NAMES = tuple(ordered_keys)
        FUNCTION = "map"
        CATEGORY = "Wizdroid/Utils/Data"

        def map(self, merged_json: str):
            try:
                import json
                data = json.loads(merged_json) if merged_json and merged_json.strip() else {}
                if not isinstance(data, dict):
                    data = {}
            except Exception:
                data = {}

            outputs: List[Any] = []
            # For each key, produce a string value suitable for the outfit node
            for key in ordered_keys:
                if key == "inputs_json":
                    # pass-through original JSON for one-cable wiring
                    outputs.append(merged_json or "")
                    continue
                val = data.get(key)
                if val is None:
                    # default control values for selectors; empty string for freeform text
                    if key in ("character_name", "custom_attributes", "makeup_data", "avoid_terms"):
                        outputs.append("")
                    else:
                        outputs.append("random")
                else:
                    outputs.append(str(val))

            return tuple(outputs)

    OutfitInputsFromJSON.__name__ = f"{gender.capitalize()}OutfitInputsFromJSONNode"
    return OutfitInputsFromJSON, OutfitInputsFromJSON.__name__


# Registration
NODE_CLASS_MAPPINGS: Dict[str, Any] = {}
NODE_DISPLAY_NAME_MAPPINGS: Dict[str, str] = {}

base = Path(__file__).resolve().parents[1]
genders = discover_genders(base / "data" / "outfit")
for g in genders:
    Node, name = create_bridge_node(g)
    NODE_CLASS_MAPPINGS[name] = Node
    NODE_DISPLAY_NAME_MAPPINGS[name] = f"🧾 {g.capitalize()} Outfit Inputs From JSON"
