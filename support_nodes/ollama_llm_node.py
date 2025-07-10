import requests
import json
import os
import random
from typing import Any, Dict, List, Tuple

class OllamaLLMNode:
    """
    Professional prompt generation engine for ComfyUI utilizing a local Ollama LLM.
    Designed for advanced users requiring fine-grained control and customization.
    All dropdown options are loaded from structured JSON files for maximum flexibility.
    """

    @staticmethod
    def load_json(file_path: str, default: Any = None) -> Any:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[OllamaLLMNode] Error loading {file_path}: {e}")
            return default if default is not None else []

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """
        Defines the input fields for the ComfyUI node, loading all dropdowns from organized JSON files.
        Advanced users can extend or modify the JSON files for custom workflows.
        """
        base_dir = os.path.dirname(__file__)
        data_dir = os.path.join(base_dir, '..', 'data')
        styles_dir = os.path.join(data_dir, 'styles')
        # Load dropdowns with user-friendly fallback
        def safe_load(path: str, default: Any) -> Any:
            data = cls.load_json(path, default)
            if not data:
                print(f"[OllamaLLMNode] Warning: Could not load {path}, using default.")
                return default
            return data
        scene_highlights = safe_load(os.path.join(styles_dir, 'scene_highlights.json'), {})
        detail_scales = safe_load(os.path.join(styles_dir, 'detail_scales.json'), ["none"])
        creative_modes = safe_load(os.path.join(styles_dir, 'creative_modes.json'), ["standard"])
        prompt_styles = ["none", "cinematic", "artistic", "photographic", "surreal", "minimalist"]
        installed_models = cls.get_ollama_models("http://127.0.0.1:11434/api/generate")
        return {
            "required": {
                "keywords": ("STRING", {"multiline": True, "default": ""}),
                "model_name": (["disabled"] + installed_models, {"default": "disabled"}),
                "prompt_style": (prompt_styles, {"default": "none"}),
                "scene_mood": (["none"] + scene_highlights.get("moods", []), {"default": "none"}),
                "scene_time": (["none"] + scene_highlights.get("times", []), {"default": "none"}),
                "scene_weather": (["none"] + scene_highlights.get("weather", []), {"default": "none"}),
                "color_scheme": (["none"] + scene_highlights.get("color_schemes", []), {"default": "none"}),
                "detail_scale": (detail_scales, {"default": "none"}),
                "creative_mode": (creative_modes, {"default": "standard"}),
            },
            "optional": {
                "custom_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999}),
                "ollama_url": ("STRING", {"default": "http://127.0.0.1:11434/api/generate"}),
            },
        }

    @staticmethod
    def get_ollama_models(ollama_url: str) -> List[str]:
        try:
            tags_url = ollama_url.replace("/api/generate", "/api/tags")
            response = requests.get(tags_url, timeout=5)
            response.raise_for_status()
            return [m["name"] for m in response.json().get("models", [])]
        except Exception as e:
            print(f"[OllamaLLMNode] Could not fetch Ollama models: {e}")
            return []

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("enhanced_prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "👗 Outfit/Support"
    NAME = "Ollama Prompter"

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
        Generates a professional, highly detailed prompt for image generation.
        Designed for advanced users who require precision and control over prompt construction.
        """
        if seed > 0:
            random.seed(seed)
        # Compose the base prompt
        prompt_parts: List[str] = [keywords.strip()]
        if custom_prompt.strip():
            prompt_parts.append(custom_prompt.strip())
        if scene_mood != "none":
            prompt_parts.append(f"{scene_mood} mood")
        if scene_time != "none":
            prompt_parts.append(f"{scene_time}")
        if scene_weather != "none":
            prompt_parts.append(f"{scene_weather}")
        if color_scheme != "none":
            prompt_parts.append(f"{color_scheme} color scheme")
        final_keywords = ", ".join([p for p in prompt_parts if p])
        # Load instructions from styles directory
        base_dir = os.path.dirname(__file__)
        data_dir = os.path.join(base_dir, '..', 'data')
        styles_dir = os.path.join(data_dir, 'styles')
        scale_instructions = self.load_json(os.path.join(styles_dir, 'scale_instructions.json'), {})
        creative_mode_instructions = self.load_json(os.path.join(styles_dir, 'creative_mode_instructions.json'), {})
        system_parts: List[str] = [
            "Focus exclusively on constructing a detailed, artistic prompt for image generation. Do not include meta-commentary or statements about AI capabilities.",
            "Utilize precise, vivid, and professional language suitable for advanced image generation workflows.",
            scale_instructions.get(detail_scale, ""),
            creative_mode_instructions.get(creative_mode, "")
        ]
        if prompt_style != "none":
            system_parts.append(f"Prompt style: {prompt_style}")
        system_prompt = "\n".join([s for s in system_parts if s])
        if model_name == "disabled" or not final_keywords:
            return (final_keywords,)
        payload: Dict[str, Any] = {
            "model": model_name,
            "system": system_prompt,
            "prompt": final_keywords,
            "stream": False,
            "options": {"seed": seed}
        }
        try:
            response = requests.post(ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            response_json = response.json()
            final_prompt = response_json.get("response", "").strip().strip('"').strip("'")
            return (final_prompt,)
        except requests.exceptions.RequestException as e:
            print(f"[OllamaLLMNode] HTTP error during prompt generation: {e}")
            return (f"ERROR: HTTP error: {e}",)
        except Exception as e:
            print(f"[OllamaLLMNode] Unexpected error during prompt generation: {e}")
            return (f"ERROR: {e}",)
