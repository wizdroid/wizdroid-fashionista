import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.prompt_builder import PromptBuilder


def test_prompt_builder_basic():
    seed = 42
    body_parts = ["torso", "legs", "headgear"]
    data = {
        "character_name": "Ava",
        "age_group": "young adult (20-29 years)",
        "race": "East Asian",
        "body_type": "athletic",
        "torso": "t-shirt",
        "legs": "jeans",
        "headgear": "beanie",
        "pose": "standing",
        "background": "Urban rooftop",
        "mood": "dramatic",
        "time_of_day": "golden hour",
        "weather": "windy",
        "color_scheme": "cool tones",
        "description_style": "sdxl",
        "creative_scale": "detailed",
        "custom_attributes": "high contrast, crisp focus",
    }
    options = {k: ["none", "random", v] for k, v in data.items() if isinstance(v, str)}

    pb = PromptBuilder(seed=seed, data=data, options=options)
    prompt = pb.build(body_parts)

    assert "Character: Ava" in prompt
    assert "Age:" in prompt and "Race:" in prompt and "Body type:" in prompt
    assert "Attire:" in prompt
    assert "Pose:" in prompt and "Background:" in prompt
    assert "Mood:" in prompt and "Time:" in prompt and "Weather:" in prompt
    assert "Color scheme:" in prompt and "Style:" in prompt and "Scale:" in prompt
    assert "Additional: high contrast, crisp focus" in prompt
