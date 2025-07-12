"""
Base utilities for Ollama-based nodes in ComfyUI Outfit Selection.
Provides common functionality for LLM and Vision nodes.
"""

import json
from typing import Any, Dict, List, Optional

import requests


class BaseOllamaNode:
    """
    Base class for Ollama nodes providing common functionality.
    """
    
    @staticmethod
    def get_ollama_models(ollama_url: str, timeout: int = 5) -> List[str]:
        """
        Fetch available Ollama models from the API.
        
        Args:
            ollama_url: Base Ollama API URL
            timeout: Request timeout in seconds
            
        Returns:
            List of available model names
        """
        try:
            tags_url = ollama_url.replace("/api/generate", "/api/tags")
            response = requests.get(tags_url, timeout=timeout)
            response.raise_for_status()
            models_data = response.json()
            return [model["name"] for model in models_data.get("models", [])]
        except Exception as e:
            print(f"[BaseOllamaNode] Could not fetch Ollama models: {e}")
            return []
    
    @staticmethod
    def load_json_data(file_path: str, default: Any = None) -> Any:
        """
        Load JSON data from file with error handling.
        
        Args:
            file_path: Path to JSON file
            default: Default value if loading fails
            
        Returns:
            Loaded JSON data or default value
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[BaseOllamaNode] Error loading {file_path}: {e}")
            return default if default is not None else {}
    
    @staticmethod
    def make_ollama_request(
        url: str, 
        payload: Dict[str, Any], 
        timeout: int = 60
    ) -> Optional[Dict[str, Any]]:
        """
        Make a request to Ollama API with error handling.
        
        Args:
            url: API endpoint URL
            payload: Request payload
            timeout: Request timeout in seconds
            
        Returns:
            Response JSON or None if failed
        """
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[BaseOllamaNode] HTTP error during request: {e}")
            return None
        except Exception as e:
            print(f"[BaseOllamaNode] Unexpected error during request: {e}")
            return None
    
    @staticmethod
    def build_system_prompt(components: List[str]) -> str:
        """
        Build system prompt from components, filtering empty strings.
        
        Args:
            components: List of prompt components
            
        Returns:
            Combined system prompt
        """
        return "\n".join(component for component in components if component.strip())
    
    @staticmethod
    def validate_model_selection(model_name: str, available_models: List[str]) -> bool:
        """
        Validate that selected model is available.
        
        Args:
            model_name: Selected model name
            available_models: List of available models
            
        Returns:
            True if model is valid and available
        """
        if model_name == "disabled":
            return False
        
        if not available_models:
            print("[BaseOllamaNode] No models available")
            return False
        
        if model_name not in available_models:
            print(f"[BaseOllamaNode] Model '{model_name}' not found in available models")
            return False
        
        return True
