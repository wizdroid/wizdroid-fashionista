# Support nodes for ComfyUI Outfit Selection
from .ollama_vision_node import OllamaVisionNode
from .ollama_llm_node import OllamaLLMNode
from .simple_ollama_node import SimpleOllamaNode

SUPPORT_NODE_CLASS_MAPPINGS = {
    "OllamaVisionNode": OllamaVisionNode,
    "OllamaLLMNode": OllamaLLMNode,
    "SimpleOllamaNode": SimpleOllamaNode
}

SUPPORT_NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaVisionNode": "👁️ Ollama Vision Describer",
    "OllamaLLMNode": "✨ Ollama Prompter",
    "SimpleOllamaNode": "🎯 Simple Ollama Prompter"
}
