# __init__.py for comfyui-outfit

# Tell ComfyUI where to find our web assets
WEB_DIRECTORY = "web"

from .dynamic_outfit_node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# Import support nodes
try:
    from .support_nodes import SUPPORT_NODE_CLASS_MAPPINGS, SUPPORT_NODE_DISPLAY_NAME_MAPPINGS
    
    # Merge the mappings
    NODE_CLASS_MAPPINGS.update(SUPPORT_NODE_CLASS_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(SUPPORT_NODE_DISPLAY_NAME_MAPPINGS)
    
    print("ComfyUI Outfit: Successfully loaded support nodes (Ollama Vision & LLM)")
except ImportError as e:
    print(f"ComfyUI Outfit: Support nodes not available (missing dependencies): {e}")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
