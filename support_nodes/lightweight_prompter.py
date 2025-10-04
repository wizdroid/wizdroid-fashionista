"""
Lightweight Prompter Node for ComfyUI Outfit Selection.
Uses lightweight models like Microsoft Phi for local prompt enhancement without requiring Ollama.
"""

import json
import logging
from typing import Any, Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LightweightPrompterNode:
    """
    Lightweight prompt enhancement using local transformer models.
    Supports Microsoft Phi, TinyLlama, and other small language models.
    """
    
    # Model configurations
    AVAILABLE_MODELS = {
        "microsoft/Phi-3-mini-4k-instruct": {
            "name": "Phi-3 Mini",
            "size": "3.8B",
            "description": "Microsoft's efficient small model"
        },
        "microsoft/Phi-3.5-mini-instruct": {
            "name": "Phi-3.5 Mini", 
            "size": "3.8B",
            "description": "Latest Phi model with improved capabilities"
        },
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0": {
            "name": "TinyLlama",
            "size": "1.1B", 
            "description": "Ultra-lightweight chat model"
        },
        "Qwen/Qwen2-1.5B-Instruct": {
            "name": "Qwen2 1.5B",
            "size": "1.5B",
            "description": "Efficient multilingual model"
        }
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input types for the ComfyUI node interface."""
        model_choices = ["disabled"] + list(cls.AVAILABLE_MODELS.keys())
        
        return {
            "required": {
                "custom_data": ("STRING", {"multiline": True, "default": ""}),
                "model_name": (model_choices, {"default": "disabled"}),
                "prompt_style": (["SDXL", "Flux", "Natural"], {"default": "SDXL"}),
                "enhancement_strength": (["light", "medium", "strong"], {"default": "medium"}),
            },
            "optional": {
                "max_length": ("INT", {"default": 150, "min": 50, "max": 500}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.1, "max": 2.0, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("enhanced_prompt",)
    FUNCTION = "enhance_prompt"
    CATEGORY = "Wizdroid/AI/LLM"
    NAME = "🚀 Lightweight Prompter"

    def __init__(self):
        """Initialize the node."""
        self.model = None
        self.tokenizer = None
        self.current_model = None
        
    def _load_model(self, model_name: str) -> bool:
        """Load the specified model and tokenizer."""
        try:
            # Import transformers only when needed
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            if self.current_model == model_name and self.model is not None:
                return True
                
            logger.info(f"Loading model: {model_name}")
            
            # Determine device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True,
                padding_side="left"
            )
            
            # Add pad token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with appropriate settings for smaller models
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                low_cpu_mem_usage=True,
                offload_folder="./offload" if device == "cpu" else None
            )
            
            if device == "cpu":
                self.model = self.model.to(device)
                
            self.current_model = model_name
            logger.info(f"Successfully loaded {model_name} on {device}")
            return True
            
        except ImportError as e:
            logger.error(f"Missing required dependencies: {e}")
            logger.info("Please install: pip install transformers torch")
            return False
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return False

    def enhance_prompt(
        self,
        custom_data: str,
        model_name: str = "disabled",
        prompt_style: str = "SDXL", 
        enhancement_strength: str = "medium",
        max_length: int = 150,
        temperature: float = 0.7,
        seed: int = 0,
    ) -> Tuple[str]:
        """
        Enhance the input prompt using lightweight language models.
        """
        # Set seed for reproducibility
        if seed > 0:
            import torch
            import random
            import numpy as np
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)
        
        # Validate inputs
        if not custom_data.strip():
            return ("",)
            
        # Handle disabled model case
        if model_name == "disabled":
            return self._format_without_model(custom_data, prompt_style)
            
        # Try to load and use the model
        if self._load_model(model_name):
            return self._generate_enhanced_prompt(
                custom_data, 
                prompt_style, 
                enhancement_strength,
                max_length, 
                temperature
            )
        else:
            # Fallback to basic formatting
            return self._format_without_model(custom_data, prompt_style)

    def _format_without_model(self, custom_data: str, prompt_style: str) -> Tuple[str]:
        """Format prompt without model enhancement."""
        formatted_data = custom_data.strip()
        
        if prompt_style == "Flux":
            # Flux prefers natural language
            if not formatted_data.startswith(("A ", "An ", "The ")):
                formatted_data = f"A detailed image of {formatted_data}"
        elif prompt_style == "Natural":
            # Keep as natural description
            pass
        else:
            # SDXL format - ensure proper punctuation
            if not formatted_data.endswith(('.', '!', '?')):
                formatted_data += "."
                
        return (formatted_data,)

    def _generate_enhanced_prompt(
        self,
        custom_data: str,
        prompt_style: str,
        enhancement_strength: str,
        max_length: int,
        temperature: float
    ) -> Tuple[str]:
        """Generate enhanced prompt using the loaded model."""
        try:
            import torch
            
            # Ensure model and tokenizer are loaded
            if self.model is None or self.tokenizer is None:
                logger.error("Model or tokenizer not loaded")
                return self._format_without_model(custom_data, prompt_style)
            
            # Build system prompt based on style and strength
            system_prompt = self._build_system_prompt(prompt_style, enhancement_strength)
            
            # Format the input for the model
            if self.current_model and "Phi-3" in self.current_model:
                # Use Phi-3 chat format
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": custom_data}
                ]
                formatted_input = self.tokenizer.apply_chat_template(
                    messages, 
                    tokenize=False, 
                    add_generation_prompt=True
                )
            else:
                # Use simple format for other models
                formatted_input = f"{system_prompt}\n\nInput: {custom_data}\nEnhanced prompt:"
            
            # Tokenize
            inputs = self.tokenizer(
                formatted_input,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            
            # Move to same device as model
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:], 
                skip_special_tokens=True
            ).strip()
            
            # Clean up response
            response = self._clean_response(response)
            
            return (response,) if response else self._format_without_model(custom_data, prompt_style)
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return self._format_without_model(custom_data, prompt_style)

    def _build_system_prompt(self, prompt_style: str, enhancement_strength: str) -> str:
        """Build system prompt based on style and enhancement strength."""
        base_instruction = "You are an expert at enhancing image generation prompts."
        
        style_instructions = {
            "SDXL": [
                "Transform the input into a detailed, descriptive SDXL prompt.",
                "Use comma-separated descriptive phrases.",
                "Focus on visual details, artistic style, lighting, and composition.",
                "Keep prompts concise but descriptive."
            ],
            "Flux": [
                "Transform the input into a natural, vivid description for Flux.",
                "Use complete, flowing sentences that read naturally.",
                "Be specific about colors, actions, and scene details.",
                "Start with the main subject, then describe environment and mood."
            ],
            "Natural": [
                "Enhance the description while keeping it natural and readable.",
                "Add relevant visual details and atmospheric elements.",
                "Maintain a conversational, descriptive tone."
            ]
        }
        
        strength_modifiers = {
            "light": "Make minimal enhancements, focusing on clarity and basic details.",
            "medium": "Add good visual details and improve descriptiveness moderately.",
            "strong": "Significantly enhance with rich details, mood, and artistic elements."
        }
        
        instructions = [base_instruction]
        instructions.extend(style_instructions.get(prompt_style, style_instructions["SDXL"]))
        instructions.append(strength_modifiers.get(enhancement_strength, strength_modifiers["medium"]))
        instructions.extend([
            "Output only the enhanced prompt without explanations.",
            "Do not add quotation marks or meta-commentary."
        ])
        
        return " ".join(instructions)

    def _clean_response(self, response: str) -> str:
        """Clean and format the model response."""
        # Remove common artifacts
        response = response.strip()
        response = response.strip('"').strip("'")
        
        # Remove any trailing explanations
        if "\n" in response:
            response = response.split("\n")[0]
            
        # Remove common prompt artifacts
        artifacts = [
            "Enhanced prompt:",
            "Prompt:",
            "Description:",
            "Image prompt:",
            "Generated prompt:"
        ]
        
        for artifact in artifacts:
            if response.startswith(artifact):
                response = response[len(artifact):].strip()
                
        return response