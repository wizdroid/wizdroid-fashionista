# Support nodes for ComfyUI Outfit Selection
from .ollama_llm import OptimizedOllamaLLMNode
from .simple_ollama import OptimizedSimpleOllamaNode
from .style_helper import PhotoStyleHelperNode
from .preset_patch_applier import PresetPatchApplierNode
from .outfit_inputs_from_json import NODE_CLASS_MAPPINGS as JSON_NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as JSON_NODE_DISPLAY

# Try to import vision node - it has additional dependencies
try:
    from .ollama_vision import OptimizedOllamaVisionNode
    VISION_NODE_AVAILABLE = True
except ImportError as e:
    print(f"[ComfyUI-Outfit] Vision node not available (missing dependencies): {e}")
    VISION_NODE_AVAILABLE = False

SUPPORT_NODE_CLASS_MAPPINGS = {
    "OllamaLLMNode": OptimizedOllamaLLMNode,
    "SimpleOllamaNode": OptimizedSimpleOllamaNode,
    "PhotoStyleHelperNode": PhotoStyleHelperNode,
    "PresetPatchApplierNode": PresetPatchApplierNode,
}

SUPPORT_NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaLLMNode": "✨ Ollama Prompter",
    "SimpleOllamaNode": "🎯 Simple Ollama",
    "PhotoStyleHelperNode": "📸 Photo Style Helper",
    "PresetPatchApplierNode": "🧩 Preset Patch Applier",
}

# Add vision node if available
if VISION_NODE_AVAILABLE:
    SUPPORT_NODE_CLASS_MAPPINGS["OllamaVisionNode"] = OptimizedOllamaVisionNode
    SUPPORT_NODE_DISPLAY_NAME_MAPPINGS["OllamaVisionNode"] = "👁️ Ollama Vision"

# Merge JSON bridge nodes (per gender)
SUPPORT_NODE_CLASS_MAPPINGS.update(JSON_NODE_CLASS_MAPPINGS)
SUPPORT_NODE_DISPLAY_NAME_MAPPINGS.update(JSON_NODE_DISPLAY)
