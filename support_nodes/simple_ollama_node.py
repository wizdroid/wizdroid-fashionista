import requests
import json
from typing import Any, Dict, List, Tuple

class SimpleOllamaNode:
    """
    Simple Ollama prompt formatter with 3 inputs: custom data, model selection, and prompt style.
    Supports SDXL (weighted prompts) and Flux (single sentence descriptions) formatting.
    """

    @staticmethod
    def get_ollama_models(ollama_url: str) -> List[str]:
        try:
            tags_url = ollama_url.replace("/api/generate", "/api/tags")
            response = requests.get(tags_url, timeout=5)
            response.raise_for_status()
            return [m["name"] for m in response.json().get("models", [])]
        except Exception as e:
            print(f"[SimpleOllamaNode] Could not fetch Ollama models: {e}")
            return []

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """
        Simple input types: custom data, model selection, and prompt style.
        """
        installed_models = cls.get_ollama_models("http://127.0.0.1:11434/api/generate")
        prompt_styles = ["SDXL", "Flux"]
        
        return {
            "required": {
                "custom_data": ("STRING", {"multiline": True, "default": ""}),
                "model_name": (["disabled"] + installed_models, {"default": "disabled"}),
                "prompt_style": (prompt_styles, {"default": "SDXL"}),
            },
            "optional": {
                "ollama_url": ("STRING", {"default": "http://127.0.0.1:11434/api/generate"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted_prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "👗 Outfit/Support"
    NAME = "Simple Ollama Prompter"

    def generate_prompt(
        self,
        custom_data: str,
        model_name: str = "disabled",
        prompt_style: str = "SDXL",
        ollama_url: str = "http://127.0.0.1:11434/api/generate",
    ) -> Tuple[str]:
        """
        Generates a formatted prompt based on the selected style.
        """
        if not custom_data.strip():
            return ("",)
        
        # If model is disabled, return the custom data as-is
        if model_name == "disabled":
            return (custom_data.strip(),)
        
        # Create system prompt based on style
        if prompt_style == "SDXL":
            system_prompt = """You are a prompt formatter. Convert the input into clean SDXL-style format. Rules:
1. Use comma-separated elements only
2. Apply weights with parentheses and colons: (element:1.2)
3. Keep weights between 0.5-1.5
4. No extra text, explanations, or prefixes
5. Output ONLY the formatted prompt

Examples:
Input: "woman with red lipstick and leather boots"
Output: woman, (red lipstick:1.1), (leather boots:1.2)

Format the following input now:"""
        
        elif prompt_style == "Flux":
            system_prompt = """You are a makeup and fashion prompt specialist. Convert the input into a single vivid descriptive sentence for Flux image generation, with special emphasis on makeup details, body shape, and how clothing complements the figure.

Rules:
1. Write ONE complete sentence only
2. ALWAYS describe makeup with specific colors, intensities, and materials (e.g., "glossy crimson lipstick", "subtle bronze eyeshadow", "shimmering gold highlighter")
3. Include body shape descriptions that complement the clothing choices (e.g., "curvaceous silhouette", "athletic build", "petite frame", "statuesque figure", "lean physique")
4. Describe how clothing fits and flatters the body type (e.g., "form-fitting dress that accentuates curves", "tailored jacket that broadens shoulders", "flowing fabric that creates graceful movement")
5. Include skin tone, lighting, and texture details
6. Use descriptive adjectives for makeup: matte, glossy, shimmering, metallic, natural, bold, subtle, dramatic, dewy, satiny, pearlescent
7. Mention specific makeup placement: eyelids, cheeks, lips, brows, lashes, temples, bridge of nose
8. Describe how makeup enhances facial features and complements the overall look
9. No extra text or explanations
10. Output ONLY the sentence

Examples:
Input: "woman with red lipstick and leather boots"
Output: A confident woman with a curvaceous silhouette and glossy crimson lipstick that enhances her full lips wears sleek leather boots that elongate her legs, standing gracefully in warm natural lighting that highlights her flawless complexion.

Input: "woman with bold smoky eyeshadow, glossy nude lipstick, and black dress"
Output: An elegant woman with a statuesque figure and dramatically bold charcoal smoky eyeshadow blended seamlessly across her eyelids and glossy nude lipstick wears a form-fitting black dress that accentuates her curves in sophisticated studio lighting that emphasizes her striking features.

Input: "man with subtle foundation, groomed eyebrows, and casual shirt"
Output: A well-groomed man with an athletic build and subtle matte foundation that evens his skin tone and perfectly shaped eyebrows wears a casual shirt that flatters his broad shoulders in natural daylight that showcases his refined masculine features.

Input: "woman with golden eyeshadow and pink blush"
Output: A radiant woman with a petite frame and shimmering golden eyeshadow that catches the light on her eyelids and soft pink blush that adds warmth to her delicate cheekbones is photographed in gentle morning light that highlights her graceful proportions.

Input: "man with fitted suit and clean-shaven face"
Output: A distinguished man with a lean physique and smooth, clean-shaven complexion wears a perfectly tailored suit that emphasizes his refined silhouette in professional lighting that accentuates his sharp jawline and confident posture.

IMPORTANT: Always describe makeup details vividly and naturally, include body shape descriptions that complement the clothing choices, and explain how garments flatter and enhance the subject's natural figure and beauty.

Convert the following input now:"""
        
        else:
            system_prompt = "Format the input as a detailed image generation prompt."
        
        # Prepare the API payload
        payload: Dict[str, Any] = {
            "model": model_name,
            "system": system_prompt,
            "prompt": custom_data.strip(),
            "stream": False,
        }
        
        try:
            response = requests.post(ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            response_json = response.json()
            formatted_prompt = response_json.get("response", "").strip().strip('"').strip("'")
            
            return (formatted_prompt,)
            
        except requests.exceptions.RequestException as e:
            print(f"[SimpleOllamaNode] HTTP error during prompt generation: {e}")
            return (f"ERROR: HTTP error: {e}",)
        except Exception as e:
            print(f"[SimpleOllamaNode] Unexpected error during prompt generation: {e}")
            return (f"ERROR: {e}",)
