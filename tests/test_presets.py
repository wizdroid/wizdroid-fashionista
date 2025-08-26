import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.common import apply_preset
from utils.data_loader import load_presets


def test_apply_preset_partial_fill():
    data_dir = ROOT / "data"
    presets = load_presets(data_dir)
    glam = presets.get("female", {}).get("Glam Party", {})

    current = {
        "preset": "Glam Party",
        "torso": "random",
        "legs": "",
        "feet": "none",
        "background": "Urban rooftop",  # keep existing, preset should not override
    }

    merged = apply_preset(current, glam)
    assert merged["torso"] == glam["torso"]
    assert merged["legs"] == glam["legs"]
    assert merged["feet"] == glam["feet"]
    # shouldn't override non-control value
    assert merged["background"] == "Urban rooftop"
