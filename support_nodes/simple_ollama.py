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
                "prompt_style": (["SDXL", "Flux"], {"default": "SDXL"}),
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
        Generate formatted prompt based on the selected style.
        
        Args:
            custom_data: Input data to format
            model_name: Selected Ollama model
            prompt_style: Formatting style (SDXL/Flux)
            ollama_url: Ollama API URL
            
        Returns:
            Tuple containing formatted prompt
        """
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
        
        # Generate LLM-enhanced prompt
        return self._generate_llm_prompt(custom_data, model_name, prompt_style, ollama_url)
    
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
        ollama_url: str
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
        else:
            system_prompt = self._build_sdxl_system_prompt()
        
        payload = {
            "model": model_name,
            "system": system_prompt,
            "prompt": custom_data,
            "stream": False,
        }
        
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
            "Do not include explanations or meta-commentary."
        ]
        return self.build_system_prompt(components)
    
    def _build_flux_system_prompt(self) -> str:
        """Build system prompt for Flux formatting."""
        components = [
            "You are an expert at creating Flux image generation prompts.",
            "Transform the input into a natural, flowing description suitable for Flux.",
            "Use complete sentences that read naturally.",
            "Focus on the overall scene, mood, and atmosphere.",
            "Keep descriptions concise but evocative.",
            "Do not include explanations or meta-commentary."
        ]
        return self.build_system_prompt(components)
