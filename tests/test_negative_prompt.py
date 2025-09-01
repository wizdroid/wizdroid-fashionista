import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.prompt_builder import PromptBuilder


def test_auto_negative_prompt_conflicts():
    seed = 123
    body_parts = ["hairstyle", "facial_hair", "eyewear"]
    data = {
        "hairstyle": "long hair",
        "facial_hair": "clean shaven",
        "eyewear": "no eyewear",
        "avoid_terms": "low-res, blurry",  # duplicates on purpose
    }
    options = {
        "hairstyle": ["none", "random", "long hair", "shaved head"],
        "facial_hair": ["none", "random", "clean shaven", "full beard"],
        "eyewear": ["none", "random", "no eyewear", "glasses"],
    }

    pb = PromptBuilder(seed=seed, data=data, options=options)
    _ = pb.build(body_parts)
    neg = pb.get_negative_prompt()

    # Should include conflict-driven negatives without duplication
    assert "beard" in neg and "mustache" in neg
    assert "low-res" in neg and "blurry" in neg
    # Should avoid duplicates
    assert neg.count("low-res") == 1


def test_seed_determinism_for_random_choices():
    seed = 999
    body_parts = ["torso", "legs"]
    data = {"torso": "random", "legs": "random"}
    options = {
        "torso": ["none", "random", "t-shirt", "hoodie", "jacket"],
        "legs": ["none", "random", "jeans", "shorts", "trousers"],
    }

    pb1 = PromptBuilder(seed=seed, data=dict(data), options=options)
    prompt1 = pb1.build(body_parts)

    pb2 = PromptBuilder(seed=seed, data=dict(data), options=options)
    prompt2 = pb2.build(body_parts)

    assert prompt1 == prompt2, "Random selections should be deterministic for same seed"
