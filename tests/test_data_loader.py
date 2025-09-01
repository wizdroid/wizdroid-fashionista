import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.data_loader import discover_body_parts, load_outfit_data, load_body_types


def test_body_parts_and_options():
    base = Path(__file__).resolve().parent.parent / "data" / "outfit" / "male"
    parts = discover_body_parts(base)
    assert "torso" in parts and "legs" in parts and "headgear" in parts

    options = load_outfit_data(base, parts)
    # ensure control options exist and non-empty
    for part, opts in options.items():
        assert opts[:2] == ["none", "random"], f"{part} missing control options"
        assert len(opts) >= 3, f"{part} should have at least one real option"


def test_body_types():
    base = Path(__file__).resolve().parent.parent / "data" / "outfit" / "female"
    types = load_body_types(base)
    assert types[:2] == ["none", "random"]
    assert any(t for t in types if t not in ("none", "random"))


def test_glamour_options_present():
    data_root = Path(__file__).resolve().parent.parent / "data" / "outfit"
    # Female torso should include at least one glam dress
    with open(data_root / "female" / "torso.json", "r", encoding="utf-8") as f:
        ft = json.load(f)
    ftypes = {item.get("type", "") for item in ft.get("attire", []) if isinstance(item, dict)}
    assert any("sequin" in t or "cocktail" in t or "bodycon" in t for t in ftypes)

    # Male torso/legs include glam variants
    with open(data_root / "male" / "torso.json", "r", encoding="utf-8") as f:
        mt = json.load(f)
    mtypes_torso = {item.get("type", "") for item in mt.get("attire", []) if isinstance(item, dict)}
    assert any("sequin" in t or "velvet" in t or "satin" in t for t in mtypes_torso)

    with open(data_root / "male" / "legs.json", "r", encoding="utf-8") as f:
        ml = json.load(f)
    mtypes_legs = {item.get("type", "") for item in ml.get("attire", []) if isinstance(item, dict)}
    assert any("tuxedo" in t or "velvet" in t or "satin" in t for t in mtypes_legs)
