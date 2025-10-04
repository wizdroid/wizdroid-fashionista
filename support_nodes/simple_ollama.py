"""
Optimized Simple Ollama Node for ComfyUI Outfit Selection.
Production-ready version with proper error handling and performance optimizations.
"""

import json
from typing import Any, Dict, List, Tuple

import requests


def get_ollama_models(ollama_url: str, timeout: int = 5) -> List[str]:
    """Fetch available Ollama models from the API."""
    try:
        tags_url = ollama_url.replace("/api/generate", "/api/tags")
        response = requests.get(tags_url, timeout=timeout)
        response.raise_for_status()
        models_data = response.json()
        return [model["name"] for model in models_data.get("models", [])]
    except Exception as e:
        print(f"[SimpleOllamaNode] Could not fetch Ollama models: {e}")
        return []


class OptimizedSimpleOllamaNode:
    """
    Simple Ollama prompt formatter optimized for production use.
    Supports SDXL and Flux formatting with proper error handling.
    """
    
    @staticmethod
    def make_ollama_request(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to Ollama API."""
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[SimpleOllamaNode] Request failed: {e}")
            return {}
    
    @staticmethod
    def validate_model_selection(model_name: str, available_models: List[str]) -> bool:
        """Validate model selection."""
        return model_name in available_models if available_models else True
    
    @staticmethod
    def build_system_prompt(components: List[str]) -> str:
        """Build system prompt from components."""
        return "\n".join(components)

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input types for the ComfyUI node interface."""
        # Cache models to avoid repeated API calls
        if not hasattr(cls, '_cached_models'):
            cls._cached_models = get_ollama_models("http://127.0.0.1:11434/api/generate")

        return {
            "required": {
                "custom_data": ("STRING", {"multiline": True, "default": ""}),
                "model_name": (["disabled"] + cls._cached_models, {"default": "disabled"}),
                "prompt_style": (["SDXL", "Flux", "Flux Kontext"], {"default": "SDXL"}),
            },
            "optional": {
                "ollama_url": ("STRING", {"default": "http://127.0.0.1:11434/api/generate"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted_prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "Wizdroid/AI/LLM"
    NAME = "Simple Ollama Prompter"

    def generate_prompt(
        self,
        custom_data: str,
        model_name: str = "disabled",
        prompt_style: str = "SDXL",
        ollama_url: str = "http://127.0.0.1:11434/api/generate",
        seed: int = 0,
    ) -> Tuple[str]:
        """
        Generate formatted prompt based on the selected style.
        Adds a random seed option for reproducibility/randomness.
        """
        import random
        # Set random seed if provided
        if seed and seed > 0:
            random.seed(seed)

        # Validate inputs
        if not custom_data.strip():
            return ("",)

        # Handle disabled model case
        if model_name == "disabled":
            return self._format_without_llm(custom_data, prompt_style)

        # Validate model availability
        available_models = get_ollama_models(ollama_url)
        if not self.validate_model_selection(model_name, available_models):
            print(f"[SimpleOllamaNode] Falling back to formatting without LLM")
            return self._format_without_llm(custom_data, prompt_style)

        # Generate LLM-enhanced prompt, passing seed
        return self._generate_llm_prompt(custom_data, model_name, prompt_style, ollama_url, seed)
    
    def _format_without_llm(self, custom_data: str, prompt_style: str) -> Tuple[str]:
        """
        Format prompt without LLM enhancement.
        
        Args:
            custom_data: Input data
            prompt_style: Formatting style
            
        Returns:
            Tuple containing formatted prompt
        """
        formatted_data = custom_data.strip()
        
        if prompt_style == "Flux":
            # Flux prefers concise, natural language
            formatted_data = formatted_data.replace(", ", " ")
            formatted_data = f"A detailed image of {formatted_data}"
        elif prompt_style == "Flux Kontext":
            # Flux Kontext preserves face/race/expression, changes other elements
            formatted_data = formatted_data.replace(", ", " ")
            formatted_data = f"A detailed image of {formatted_data}, maintaining the original facial features, race, and expression"
        else:
            # SDXL uses weighted prompt format
            if not formatted_data.endswith(('.', '!', '?')):
                formatted_data += "."
        
        return (formatted_data,)
    
    def _generate_llm_prompt(
        self, 
        custom_data: str, 
        model_name: str, 
        prompt_style: str, 
        ollama_url: str,
        seed: int = 0
    ) -> Tuple[str]:
        """
        Generate LLM-enhanced prompt.
        
        Args:
            custom_data: Input data
            model_name: Model to use
            prompt_style: Formatting style
            ollama_url: API URL
            
        Returns:
            Tuple containing enhanced prompt
        """
        # Build style-specific system prompt
        if prompt_style == "Flux":
            system_prompt = self._build_flux_system_prompt()
        elif prompt_style == "Flux Kontext":
            system_prompt = self._build_flux_kontext_system_prompt()
        else:
            system_prompt = self._build_sdxl_system_prompt()
        
        payload = {
            "model": model_name,
            "system": system_prompt,
            "prompt": custom_data,
            "stream": False,
        }
        # If seed is provided, add to payload (if Ollama supports it)
        if seed and seed > 0:
            payload["options"] = {"seed": seed}
        
        response_data = self.make_ollama_request(ollama_url, payload)
        
        if response_data:
            enhanced_prompt = response_data.get("response", "").strip()
            enhanced_prompt = enhanced_prompt.strip('"').strip("'")
            return (enhanced_prompt,) if enhanced_prompt else self._format_without_llm(custom_data, prompt_style)
        
        # Fallback to non-LLM formatting
        return self._format_without_llm(custom_data, prompt_style)
    
    def _build_sdxl_system_prompt(self) -> str:
        """Build system prompt for SDXL formatting."""
        components = [
            "You are an expert at creating SDXL image generation prompts.",
            "Transform the input into a detailed, descriptive prompt suitable for SDXL.",
            "Focus on visual details, artistic style, lighting, and composition.",
            "Use comma-separated descriptive phrases.",
            "Keep prompts under 200 tokens for optimal performance.",
            "Do not include explanations or meta-commentary.",
            "Output only the prompt without any additional text.",
        ]
        return self.build_system_prompt(components)
    
    def _build_flux_system_prompt(self) -> str:
        """Build system prompt for Flux formatting."""
        components = [
            "You are an expert at creating Flux image generation prompts.",
            "Transform the input into a highly specific, natural, and vivid description suitable for Flux.",
            "Start with the main subject, then describe the environment, background, and any relevant objects.",
            "Be concrete and unambiguous: specify colors, clothing, actions, and scene details.",
            "Include style, lighting, and mood if provided or implied.",
            "Use complete, natural sentences that read like a scene from a novel.",
            "Avoid vague adjectives (like 'nice', 'beautiful'); use precise, descriptive language.",
            "Keep the prompt under 100 tokens for optimal performance.",
            "Output only the prompt without any additional text or title.",
            "Example: A young woman with short black hair sits on a wooden bench in a sunlit park, surrounded by blooming cherry blossom trees. She wears a blue denim jacket and white sneakers, reading a red book. The scene is bright and cheerful, with soft morning light and gentle shadows."
        ]
        return self.build_system_prompt(components)
    
    def _build_flux_kontext_system_prompt(self) -> str:
        """Build system prompt for Flux Kontext formatting with face/race/expression preservation."""
        components = [
            "You are an expert at creating Flux image generation prompts for outfit and scene changes while preserving identity.",
            "Transform the input into a highly specific, natural description suitable for Flux that MAINTAINS the original person's facial features, race, and expression.",
            "CRITICAL: Always preserve the subject's face, facial structure, skin tone, race, ethnicity, and emotional expression EXACTLY as described or implied.",
            "Focus on changing ONLY: hairstyle, hair color, clothing, accessories, background, environment, lighting, pose, and scene elements.",
            "Start with the main subject preserving their identity, then describe new clothing, environment, and scene details.",
            "Be concrete about outfit changes: specify colors, clothing styles, accessories, and fashion details.",
            "Include new background, lighting, and mood while keeping the person's core identity intact.",
            "Use complete, natural sentences that clearly distinguish between preserved features (face/race/expression) and changeable elements (clothes/hair/background).",
            "Keep the prompt under 100 tokens for optimal performance.",
            "Output only the prompt without any additional text or title.",
            "Example: The same person with identical facial features and expression now wears a red leather jacket and black jeans, standing in a busy city street at sunset with warm orange lighting and tall buildings in the background."
        ]
        return self.build_system_prompt(components)
