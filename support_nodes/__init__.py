# Support nodes for ComfyUI Outfit Selection
from .ollama_llm import OptimizedOllamaLLMNode
from .simple_ollama import OptimizedSimpleOllamaNode

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
}

SUPPORT_NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaLLMNode": "✨ Ollama Prompter",
    "SimpleOllamaNode": "🎯 Simple Ollama",
}

# Add vision node if available
if VISION_NODE_AVAILABLE:
    SUPPORT_NODE_CLASS_MAPPINGS["OllamaVisionNode"] = OptimizedOllamaVisionNode
    SUPPORT_NODE_DISPLAY_NAME_MAPPINGS["OllamaVisionNode"] = "👁️ Ollama Vision"
