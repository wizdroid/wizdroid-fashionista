"""
Lightweight Vision Node for ComfyUI Outfit Selection.
Uses lightweight vision models like Microsoft Florence-2, BLIP/BLIP-2, and WD14 for local image analysis.
"""

import io
import json
import logging
import os
from typing import Any, Dict, List, Tuple, Optional

import numpy as np
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LightweightVisionNode:
    """
    Lightweight vision node using local transformer models.
    Supports Microsoft Florence-2, BLIP/BLIP-2, WD14, and other vision models.
    """
    
    # Model configurations
    AVAILABLE_MODELS = {
        "microsoft/Florence-2-base": {
            "name": "Florence-2 Base",
            "size": "230M",
            "description": "Microsoft's versatile vision-language model",
            "tasks": ["caption", "detailed_caption", "more_detailed_caption", "od", "dense_region_caption"]
        },
        "microsoft/Florence-2-large": {
            "name": "Florence-2 Large", 
            "size": "770M",
            "description": "Larger Florence-2 with better performance",
            "tasks": ["caption", "detailed_caption", "more_detailed_caption", "od", "dense_region_caption"]
        },
        "Salesforce/blip-image-captioning-base": {
            "name": "BLIP Base",
            "size": "180M",
            "description": "Salesforce BLIP for image captioning",
            "tasks": ["caption"]
        },
        "Salesforce/blip-image-captioning-large": {
            "name": "BLIP Large",
            "size": "450M", 
            "description": "Larger BLIP model with better quality",
            "tasks": ["caption"]
        },
        "Salesforce/blip2-opt-2.7b": {
            "name": "BLIP-2 OPT 2.7B",
            "size": "2.7B",
            "description": "BLIP-2 with OPT language model",
            "tasks": ["caption", "vqa"]
        },
        "SmilingWolf/wd-v1-4-moat-tagger-v2": {
            "name": "WD14 Tagger",
            "size": "200M",
            "description": "Waifu Diffusion 1.4 image tagger for anime/illustrations",
            "tasks": ["tagging"]
        }
    }
    
    # Task descriptions for Florence-2
    FLORENCE_TASKS = {
        "caption": "<CAPTION>",
        "detailed_caption": "<DETAILED_CAPTION>", 
        "more_detailed_caption": "<MORE_DETAILED_CAPTION>",
        "od": "<OD>",  # Object Detection
        "dense_region_caption": "<DENSE_REGION_CAPTION>"
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input types for the ComfyUI node interface."""
        model_choices = ["disabled"] + list(cls.AVAILABLE_MODELS.keys())
        
        return {
            "required": {
                "image": ("IMAGE",),
                "model_name": (model_choices, {"default": "disabled"}),
                "task_type": (["caption", "detailed_caption", "more_detailed_caption", "tagging", "vqa"], {"default": "caption"}),
                "description_style": (["natural", "prompt", "tags", "detailed"], {"default": "natural"}),
            },
            "optional": {
                "custom_prompt": ("STRING", {"multiline": True, "default": ""}),
                "confidence_threshold": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.1}),
                "max_length": ("INT", {"default": 200, "min": 50, "max": 500}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("description",)
    FUNCTION = "analyze_image"
    CATEGORY = "Wizdroid/AI"
    NAME = "👁️ Lightweight Vision"

    def __init__(self):
        """Initialize the node."""
        self.model = None
        self.processor = None
        self.current_model = None
        self.model_type = None
        
    def _load_model(self, model_name: str) -> bool:
        """Load the specified vision model and processor."""
        try:
            if self.current_model == model_name and self.model is not None:
                return True
                
            logger.info(f"Loading vision model: {model_name}")
            
            # Import required libraries based on model type
            if "Florence" in model_name:
                from transformers import AutoProcessor, AutoModelForCausalLM
                import torch
                
                # Load Florence-2 model
                device = "cuda" if torch.cuda.is_available() else "cpu"
                
                self.processor = AutoProcessor.from_pretrained(
                    model_name, 
                    trust_remote_code=True
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                    device_map="auto" if device == "cuda" else None,
                    low_cpu_mem_usage=True
                )
                
                if device == "cpu":
                    self.model = self.model.to(device)
                    
                self.model_type = "florence"
                
            elif "blip" in model_name.lower():
                import torch
                
                device = "cuda" if torch.cuda.is_available() else "cpu"
                
                if "blip2" in model_name.lower():
                    from transformers import Blip2Processor, Blip2ForConditionalGeneration
                    self.processor = Blip2Processor.from_pretrained(model_name)
                    self.model = Blip2ForConditionalGeneration.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                        device_map="auto" if device == "cuda" else None,
                        low_cpu_mem_usage=True
                    )
                    self.model_type = "blip2"
                else:
                    from transformers import BlipProcessor, BlipForConditionalGeneration
                    self.processor = BlipProcessor.from_pretrained(model_name)
                    self.model = BlipForConditionalGeneration.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                        device_map="auto" if device == "cuda" else None,
                        low_cpu_mem_usage=True
                    )
                    self.model_type = "blip"
                
                if device == "cpu":
                    self.model = self.model.to(device)
                    
            elif "wd-" in model_name:
                # WD14 Tagger setup
                import torch
                from transformers import AutoImageProcessor, AutoModelForImageClassification
                
                device = "cuda" if torch.cuda.is_available() else "cpu"
                
                self.processor = AutoImageProcessor.from_pretrained(model_name)
                self.model = AutoModelForImageClassification.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                    device_map="auto" if device == "cuda" else None,
                    low_cpu_mem_usage=True
                )
                
                if device == "cpu":
                    self.model = self.model.to(device)
                    
                self.model_type = "wd14"
                
            else:
                logger.error(f"Unsupported model type: {model_name}")
                return False
                
            self.current_model = model_name
            logger.info(f"Successfully loaded {model_name} on {self.model.device if hasattr(self.model, 'device') else 'unknown device'}")
            return True
            
        except ImportError as e:
            logger.error(f"Missing required dependencies: {e}")
            logger.info("Please install: pip install transformers torch")
            return False
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return False

    def analyze_image(
        self,
        image,
        model_name: str = "disabled",
        task_type: str = "caption",
        description_style: str = "natural",
        custom_prompt: str = "",
        confidence_threshold: float = 0.3,
        max_length: int = 200,
        seed: int = 0,
    ) -> Tuple[str]:
        """
        Analyze the input image using lightweight vision models.
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
        if model_name == "disabled":
            return ("Vision model is disabled. Please select a model.",)
            
        # Convert tensor to PIL Image
        pil_image = self._tensor_to_pil(image)
        if pil_image is None:
            return ("Error: Could not process input image.",)
            
        # Try to load and use the model
        if self._load_model(model_name):
            return self._generate_description(
                pil_image,
                task_type,
                description_style,
                custom_prompt,
                confidence_threshold,
                max_length
            )
        else:
            return ("Error: Could not load the selected model.",)

    def _tensor_to_pil(self, tensor) -> Optional[Image.Image]:
        """Convert tensor image to PIL Image."""
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
            elif np_image.shape[-1] == 4:
                # Remove alpha channel
                np_image = np_image[:, :, :3]

            # Convert to PIL Image
            pil_image = Image.fromarray((np_image * 255).astype(np.uint8))
            return pil_image.convert("RGB")

        except Exception as e:
            logger.error(f"Error converting tensor to PIL: {e}")
            return None

    def _generate_description(
        self,
        image: Image.Image,
        task_type: str,
        description_style: str,
        custom_prompt: str,
        confidence_threshold: float,
        max_length: int
    ) -> Tuple[str]:
        """Generate description based on model type and task."""
        try:
            import torch
            
            if self.model_type == "florence":
                return self._generate_florence_description(
                    image, task_type, custom_prompt, max_length
                )
            elif self.model_type in ["blip", "blip2"]:
                return self._generate_blip_description(
                    image, task_type, custom_prompt, max_length
                )
            elif self.model_type == "wd14":
                return self._generate_wd14_tags(
                    image, confidence_threshold, description_style
                )
            else:
                return ("Error: Unknown model type.",)
                
        except Exception as e:
            logger.error(f"Description generation failed: {e}")
            return (f"Error generating description: {str(e)}",)

    def _generate_florence_description(
        self,
        image: Image.Image,
        task_type: str,
        custom_prompt: str,
        max_length: int
    ) -> Tuple[str]:
        """Generate description using Florence-2 model."""
        import torch
        
        # Map task to Florence-2 task token
        task_prompt = self.FLORENCE_TASKS.get(task_type, "<CAPTION>")
        
        # Add custom prompt if provided
        if custom_prompt.strip():
            task_prompt = f"{task_prompt} {custom_prompt}"
        
        # Process inputs
        inputs = self.processor(
            text=task_prompt,
            images=image,
            return_tensors="pt"
        )
        
        # Move to model device
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=max_length,
                num_beams=3,
                do_sample=False,
            )
        
        # Decode
        generated_text = self.processor.batch_decode(
            generated_ids, 
            skip_special_tokens=False
        )[0]
        
        # Clean up the response
        parsed_answer = self.processor.post_process_generation(
            generated_text,
            task=task_prompt,
            image_size=(image.width, image.height)
        )
        
        # Extract relevant text based on task
        if task_type in ["caption", "detailed_caption", "more_detailed_caption"]:
            result = parsed_answer.get(task_prompt, "").strip()
        else:
            # For other tasks, format the output appropriately
            result = str(parsed_answer)
            
        return (result if result else "No description generated.",)

    def _generate_blip_description(
        self,
        image: Image.Image,
        task_type: str,
        custom_prompt: str,
        max_length: int
    ) -> Tuple[str]:
        """Generate description using BLIP/BLIP-2 model."""
        import torch
        
        # Prepare inputs
        if custom_prompt.strip():
            # Conditional generation with prompt
            inputs = self.processor(image, custom_prompt, return_tensors="pt")
        else:
            # Unconditional generation
            inputs = self.processor(image, return_tensors="pt")
        
        # Move to model device
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                num_beams=5,
                do_sample=False,
                temperature=1.0,
            )
        
        # Decode
        generated_text = self.processor.decode(
            generated_ids[0], 
            skip_special_tokens=True
        ).strip()
        
        return (generated_text if generated_text else "No description generated.",)

    def _generate_wd14_tags(
        self,
        image: Image.Image,
        confidence_threshold: float,
        description_style: str
    ) -> Tuple[str]:
        """Generate tags using WD14 tagger."""
        import torch
        
        # Process image
        inputs = self.processor(image, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.sigmoid(outputs.logits)
        
        # Get labels and scores
        scores = predictions.cpu().numpy()[0]
        
        # Load label names (this would need to be implemented based on the specific WD14 model)
        # For now, we'll use placeholder logic
        labels = [f"tag_{i}" for i in range(len(scores))]
        
        # Filter by confidence threshold
        confident_tags = [
            (label, score) for label, score in zip(labels, scores)
            if score > confidence_threshold
        ]
        
        # Sort by confidence
        confident_tags.sort(key=lambda x: x[1], reverse=True)
        
        # Format output based on style
        if description_style == "tags":
            result = ", ".join([tag for tag, _ in confident_tags[:20]])
        else:
            # Convert to natural description
            top_tags = [tag for tag, _ in confident_tags[:10]]
            result = f"Image contains: {', '.join(top_tags)}"
        
        return (result if result else "No tags detected above threshold.",)