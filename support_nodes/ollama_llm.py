"""
Optimized Ollama LLM Node for ComfyUI Outfit Selection.
Professional prompt generation engine utilizing local Ollama LLM.
"""

import json
import os
import random
import requests
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_json_file(file_path: str, default: Any = None) -> Any:
    """Load a JSON file with error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        print(f"[ComfyUI-Outfit] Error loading {file_path}: {e}")
        return default if default is not None else {}


def safe_random_choice(options: List[str], exclude: List[str] = None) -> str:
    """Safely select a random choice from options, excluding specified values."""
    if not options:
        return "none"
    
    exclude = exclude or ["none", "random"]
    valid_options = [opt for opt in options if opt not in exclude]
    
    if not valid_options:
        return "none"
    
    return random.choice(valid_options)


def get_ollama_models(ollama_url: str, timeout: int = 5) -> List[str]:
    """Fetch available Ollama models from the API."""
    try:
        tags_url = ollama_url.replace("/api/generate", "/api/tags")
        response = requests.get(tags_url, timeout=timeout)
        response.raise_for_status()
        models_data = response.json()
        return [model["name"] for model in models_data.get("models", [])]
    except Exception as e:
        print(f"[OllamaLLMNode] Could not fetch Ollama models: {e}")
        return []


class OptimizedOllamaLLMNode:
    """
    Professional prompt generation engine for ComfyUI utilizing a local Ollama LLM.
    Refactored for enhanced maintainability, testability, and performance.
    """

    @classmethod
    def _get_data_directory(cls) -> str:
        """Get the data directory path."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    @staticmethod
    def build_system_prompt(components: List[str]) -> str:
        """Build system prompt from components."""
        return "\n".join(components)
    
    @staticmethod
    def make_ollama_request(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to Ollama API."""
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[OllamaLLMNode] Request failed: {e}")
            return {}

    @classmethod
    def _load_styles_data(cls) -> Dict[str, Any]:
        """Load all styles data for the node."""
        styles_dir = os.path.join(cls._get_data_directory(), "styles")
        
        return {
            "scene_highlights": load_json_file(
                os.path.join(styles_dir, "scene_highlights.json"), {}
            ),
            "detail_scales": load_json_file(
                os.path.join(styles_dir, "detail_scales.json"), ["none"]
            ),
            "creative_modes": load_json_file(
                os.path.join(styles_dir, "creative_modes.json"), ["standard"]
            ),
            "scale_instructions": load_json_file(
                os.path.join(styles_dir, "scale_instructions.json"), {}
            ),
            "creative_mode_instructions": load_json_file(
                os.path.join(styles_dir, "creative_mode_instructions.json"), {}
            ),
        }

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """
        Defines the input fields for the ComfyUI node.
        Advanced users can extend or modify the JSON files for custom workflows.
        """
        styles_data = cls._load_styles_data()
        scene_highlights = styles_data["scene_highlights"]
        detail_scales = styles_data["detail_scales"]
        creative_modes = styles_data["creative_modes"]
        
        # Standard prompt styles
        prompt_styles = [
            "none",
            "cinematic",
            "artistic",
            "photographic",
            "surreal",
            "minimalist",
        ]
        
        # Get available models
        installed_models = get_ollama_models("http://127.0.0.1:11434/api/generate")
        
        return {
            "required": {
                "keywords": ("STRING", {"multiline": True, "default": ""}),
                "model_name": (
                    ["disabled"] + installed_models,
                    {"default": "disabled"},
                ),
                "prompt_style": (prompt_styles, {"default": "none"}),
                "scene_mood": (
                    ["none"] + scene_highlights.get("moods", []),
                    {"default": "none"},
                ),
                "scene_time": (
                    ["none"] + scene_highlights.get("times", []),
                    {"default": "none"},
                ),
                "scene_weather": (
                    ["none"] + scene_highlights.get("weather", []),
                    {"default": "none"},
                ),
                "color_scheme": (
                    ["none"] + scene_highlights.get("color_schemes", []),
                    {"default": "none"},
                ),
                "detail_scale": (detail_scales, {"default": "none"}),
                "creative_mode": (creative_modes, {"default": "standard"}),
            },
            "optional": {
                "custom_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999}),
                "ollama_url": (
                    "STRING",
                    {"default": "http://127.0.0.1:11434/api/generate"},
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("enhanced_prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "👗 Outfit/Support"
    NAME = "Optimized Ollama Prompter"

    def _build_base_prompt(
        self,
        keywords: str,
        custom_prompt: str,
        scene_mood: str,
        scene_time: str,
        scene_weather: str,
        color_scheme: str,
    ) -> str:
        """Build the base prompt from user inputs."""
        prompt_parts = [keywords.strip()]
        
        if custom_prompt.strip():
            prompt_parts.append(custom_prompt.strip())
        
        # Add scene elements
        scene_elements = [
            (scene_mood, "mood"),
            (scene_time, ""),
            (scene_weather, ""),
            (color_scheme, "color scheme"),
        ]
        
        for value, suffix in scene_elements:
            if value != "none":
                part = f"{value} {suffix}".strip()
                prompt_parts.append(part)
        
        return ", ".join(part for part in prompt_parts if part)

    def _build_system_prompt(
        self,
        prompt_style: str,
        detail_scale: str,
        creative_mode: str,
        styles_data: Dict[str, Any],
    ) -> str:
        """Build the system prompt for the LLM."""
        system_components = [
            "Focus exclusively on constructing a detailed, artistic prompt for image generation.",
            "Do not include meta-commentary or statements about AI capabilities.",
            "Utilize precise, vivid, and professional language suitable for advanced image generation workflows.",
            styles_data["scale_instructions"].get(detail_scale, ""),
            styles_data["creative_mode_instructions"].get(creative_mode, ""),
        ]
        
        if prompt_style != "none":
            system_components.append(f"Prompt style: {prompt_style}")
        
        return self.build_system_prompt(system_components)

    def generate_prompt(
        self,
        keywords: str,
        model_name: str = "disabled",
        prompt_style: str = "none",
        scene_mood: str = "none",
        scene_time: str = "none",
        scene_weather: str = "none",
        color_scheme: str = "none",
        detail_scale: str = "none",
        creative_mode: str = "standard",
        custom_prompt: str = "",
        seed: int = 0,
        ollama_url: str = "http://127.0.0.1:11434/api/generate",
    ) -> Tuple[str]:
        """
        Generate a professional, highly detailed prompt for image generation.
        """
        # Set seed for reproducibility
        if seed > 0:
            random.seed(seed)
        
        # Build base prompt
        base_prompt = self._build_base_prompt(
            keywords, custom_prompt, scene_mood, scene_time, scene_weather, color_scheme
        )
        
        # Return base prompt if model is disabled or no keywords
        if model_name == "disabled" or not base_prompt:
            return (base_prompt,)
        
        # Load styles data and build system prompt
        styles_data = self._load_styles_data()
        system_prompt = self._build_system_prompt(
            prompt_style, detail_scale, creative_mode, styles_data
        )
        
        # Prepare API payload
        payload = {
            "model": model_name,
            "system": system_prompt,
            "prompt": base_prompt,
            "stream": False,
            "options": {"seed": seed},
        }
        
        # Make API call
        response_data = self.make_ollama_request(ollama_url, payload)
        
        if response_data is None:
            return (f"ERROR: Could not connect to Ollama at {ollama_url}",)
        
        # Extract and clean response
        enhanced_prompt = response_data.get("response", "").strip().strip('"').strip("'")
        
        if not enhanced_prompt:
            return (f"ERROR: Empty response from model {model_name}",)
        
        return (enhanced_prompt,)
