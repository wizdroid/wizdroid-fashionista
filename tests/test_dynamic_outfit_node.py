import sys
from pathlib import Path
import pytest

# Add project root to the Python path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nodes.dynamic_outfit import create_outfit_node
from utils.prompt_builder import PromptBuilder

@pytest.fixture(scope="module")
def female_outfit_node():
    """Fixture to create a female outfit node instance."""
    Node, _ = create_outfit_node("female")
    return Node()

def test_female_node_creation(female_outfit_node):
    """Test that the female outfit node is created successfully."""
    assert female_outfit_node is not None
    assert female_outfit_node.CATEGORY == "👗 Outfit/Female"
    assert "torso" in female_outfit_node.INPUT_TYPES()["required"]

def test_prompt_generation(female_outfit_node):
    """Test basic prompt generation."""
    inputs = {
        "seed": 123,
        "torso": "t-shirt",
        "legs": "jeans",
        "feet": "sneakers",
    }
    positive_prompt, seed, negative_prompt, metadata = female_outfit_node.process(**inputs)
    assert isinstance(positive_prompt, str)
    assert "t-shirt" in positive_prompt
    assert "jeans" in positive_prompt
    assert "sneakers" in positive_prompt
    assert seed == 123

def test_preset_application(female_outfit_node):
    """Test that presets are applied correctly."""
    inputs = {
        "preset": "Casual",
        "seed": 456,
        "torso": "random",
        "legs": "random",
    }
    # This test assumes a 'Casual' preset exists for females
    # In a real-world scenario, you might want to mock the preset data
    positive_prompt, _, _, _ = female_outfit_node.process(**inputs)
    assert "Casual" not in positive_prompt  # The preset name itself should not be in the prompt

def test_seed_modes(female_outfit_node):
    """Test different seed modes."""
    # Fixed seed
    inputs = {"seed": 789, "seed_mode": "fixed"}
    _, seed1, _, _ = female_outfit_node.process(**inputs)
    _, seed2, _, _ = female_outfit_node.process(**inputs)
    assert seed1 == seed2 == 789

    # Increment seed
    inputs = {"seed": 100, "seed_mode": "increment", "_last_seed": 100}
    _, seed3, _, _ = female_outfit_node.process(**inputs)
    assert seed3 == 101
