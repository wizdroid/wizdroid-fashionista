"""
Optimized Ollama Vision Node for ComfyUI Outfit Selection.
Enhanced image description generation using local Ollama vision models.
"""

import base64
import io
import json
import os
import random
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image


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
        print(f"[OllamaVisionNode] Could not fetch Ollama models: {e}")
        return []


class OptimizedOllamaVisionNode:
    """
    ComfyUI node for image description using local Ollama vision models.
    Refactored for enhanced maintainability, testability, and performance.
    """

    # Vision model keywords for filtering
    VISION_KEYWORDS = [
        "vision",
        "llava",
        "bakllava",
        "moondream",
        "cogvlm",
        "blip",
        "instructblip",
        "minigpt",
        "mplug",
        "qwen-vl",
    ]

    @classmethod
    def _get_data_directory(cls) -> str:
        """Get the data directory path."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    @staticmethod
    def make_ollama_request(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to Ollama API."""
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[OllamaVisionNode] Request failed: {e}")
            return {}

    @classmethod
    def get_ollama_vision_models(cls, ollama_url: str) -> List[str]:
        """
        Fetch vision-capable models from Ollama API.
        
        Args:
            ollama_url: Ollama API URL
            
        Returns:
            List of vision-capable model names
        """
        all_models = get_ollama_models(ollama_url)
        
        if not all_models:
            return []
        
        # Filter for vision-capable models
        vision_models = []
        for model in all_models:
            model_name_lower = model.lower()
            if any(keyword in model_name_lower for keyword in cls.VISION_KEYWORDS):
                vision_models.append(model)
        
        # If no vision models found, return all models (user might have renamed them)
        return vision_models if vision_models else all_models

    @classmethod
    def _load_description_prompts(cls) -> Dict[str, str]:
        """Load description prompt templates from JSON file."""
        prompts_path = os.path.join(
            cls._get_data_directory(), "styles", "description_prompts.json"
        )
        return load_json_file(prompts_path, {})

    @staticmethod
    def _tensor_to_base64(tensor) -> Optional[str]:
        """
        Convert tensor image to base64 string for API transmission.
        
        Args:
            tensor: Input image tensor
            
        Returns:
            Base64 encoded image string or None if conversion fails
        """
        try:
            # Handle batch dimension
            if tensor.dim() == 4:
                tensor = tensor.squeeze(0)

            # Convert from [C, H, W] to [H, W, C] if needed
            if tensor.dim() == 3 and tensor.shape[0] in [1, 3, 4]:
                tensor = tensor.permute(1, 2, 0)

            # Normalize to [0, 1] range
            if tensor.max() > 1.0:
                tensor = tensor / 255.0

            # Convert to numpy
            np_image = tensor.cpu().numpy()

            # Handle grayscale conversion
            if np_image.shape[-1] == 1:
                np_image = np.repeat(np_image, 3, axis=-1)

            # Convert to PIL Image
            pil_image = Image.fromarray((np_image * 255).astype(np.uint8))

            # Encode to base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode()

        except Exception as e:
            print(f"[OptimizedOllamaVisionNode] Error converting tensor to base64: {e}")
            return None

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input fields for the ComfyUI node."""
        try:
            # Get available vision models
            vision_models = cls.get_ollama_vision_models("http://127.0.0.1:11434/api/generate")
            
            # Load description prompts
            prompts = cls._load_description_prompts()
            
            return {
                "required": {
                    "image": ("IMAGE",),
                    "model_name": (
                        ["disabled"] + vision_models,
                        {"default": "disabled"},
                    ),
                    "description_style": (
                        ["none", "random"] + list(prompts.keys()),
                        {"default": "detailed"},
                    ),
                    "custom_prompt": (
                        "STRING",
                        {"multiline": True, "default": ""},
                    ),
                },
                "optional": {
                    "seed": ("INT", {"default": 0, "min": 0, "max": 999999}),
                    "ollama_url": (
                        "STRING",
                        {"default": "http://127.0.0.1:11434/api/generate"},
                    ),
                },
            }
        except Exception as e:
            print(f"[OptimizedOllamaVisionNode] CRITICAL ERROR in INPUT_TYPES: {e}")
            return {
                "required": {
                    "image": ("IMAGE",),
                    "error_message": (
                        "STRING",
                        {
                            "multiline": True,
                            "default": f"ERROR: Node failed to load. Check console: {e}",
                        },
                    ),
                }
            }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("description",)
    FUNCTION = "describe_image"
    CATEGORY = "👗 Outfit/Support"
    NAME = "Optimized Ollama Vision"

    def _select_description_style(self, description_style: str, seed: int) -> str:
        """
        Select appropriate description style, handling random selection.
        
        Args:
            description_style: Selected style or "random"
            seed: Random seed for reproducibility
            
        Returns:
            Selected description style
        """
        if description_style != "random":
            return description_style
        
        # Handle random selection
        if seed > 0:
            random.seed(seed)
        
        prompts = self._load_description_prompts()
        available_styles = [key for key in prompts.keys() if key not in ["none", "random"]]
        
        if not available_styles:
            return "detailed"
        
        return safe_random_choice(available_styles, exclude=["none", "random"])

    def _build_system_prompt(
        self, description_style: str, custom_prompt: str
    ) -> str:
        """
        Build system prompt for the vision model.
        
        Args:
            description_style: Selected description style
            custom_prompt: User's custom prompt additions
            
        Returns:
            Complete system prompt
        """
        prompts = self._load_description_prompts()
        
        # Get base prompt for the style
        base_prompt = prompts.get(description_style, prompts.get("detailed", ""))
        
        # Build system prompt components
        system_components = [base_prompt]
        
        if custom_prompt.strip():
            system_components.append(f"Custom instructions: {custom_prompt.strip()}")
        
        system_components.append(
            "Provide your response in clear, descriptive language suitable for "
            "image generation or cataloging purposes."
        )
        
        return self.build_system_prompt(system_components)

    def describe_image(
        self,
        image,
        model_name: str = "disabled",
        description_style: str = "detailed",
        custom_prompt: str = "",
        seed: int = 0,
        ollama_url: str = "http://127.0.0.1:11434/api/generate",
    ) -> Tuple[str]:
        """
        Generate description of the input image using Ollama vision model.
        
        Args:
            image: Input image tensor
            model_name: Selected vision model
            description_style: Style of description to generate
            custom_prompt: Additional custom instructions
            seed: Random seed for reproducibility
            ollama_url: Ollama API URL
            
        Returns:
            Tuple containing image description
        """
        # Validate model selection
        if model_name == "disabled":
            return ("Vision model is disabled. Please select a vision-capable model.",)
        
        # Handle "none" style selection
        if description_style == "none":
            return (
                "Please select a description style other than 'none' to generate "
                "an image description.",
            )
        
        # Convert image to base64
        img_base64 = self._tensor_to_base64(image)
        if img_base64 is None:
            return ("ERROR: Could not process the input image.",)
        
        # Select description style (handle random)
        selected_style = self._select_description_style(description_style, seed)
        
        # Build system prompt
        system_prompt = self._build_system_prompt(selected_style, custom_prompt)
        
        # Prepare API payload
        payload = {
            "model": model_name,
            "prompt": "Describe this image in detail.",
            "system": system_prompt,
            "images": [img_base64],
            "stream": False,
            "options": {
                "num_predict": 500,
                "temperature": 0.7,
                "seed": seed if seed > 0 else None,
            },
        }
        
        # Make API call
        response_data = self.make_ollama_request(ollama_url, payload, timeout=120)
        
        if response_data is None:
            return (f"ERROR: Could not connect to Ollama at {ollama_url}",)
        
        # Extract and clean response
        description = response_data.get("response", "").strip()
        description = description.strip('"').strip("'").strip()
        
        if not description:
            return ("ERROR: Received empty response from the vision model.",)
        
        print(f"[OptimizedOllamaVisionNode] Generated description: {description[:100]}...")
        return (description,)
