import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.data_loader import (
    load_presets,
    discover_body_parts,
    load_outfit_data,
    load_global_options,
)


def test_preset_values_exist_for_female():
    base = ROOT / "data" / "outfit" / "female"
    data_dir = ROOT / "data"

    presets = load_presets(data_dir).get("female", {})

    body_parts = discover_body_parts(base)
    attire_options = load_outfit_data(base, body_parts)

    # globals
    poses = load_global_options(base, "poses.json", "poses")
    bgs = load_global_options(data_dir, "backgrounds.json", "backgrounds")

    for name, preset in presets.items():
        for k, v in preset.items():
            if k in attire_options:
                assert v in attire_options[k] or v in ("none", "random"), (
                    f"Preset '{name}' for key '{k}' value '{v}' not found in options"
                )
            elif k == "pose":
                assert v in poses or v in ("none", "random"), f"Preset pose invalid: {v}"
            elif k == "background":
                assert v in bgs or v in ("none", "random"), f"Preset bg invalid: {v}"
            # others (mood/time/weather/color_scheme/makeup_data) are free-form selectors or JSON
