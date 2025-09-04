from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path

from ..utils.data_loader import (
    discover_genders,
    load_global_options,
    load_body_types,
)
from ..utils.common import load_json_file


class PhotoStyleHelperNode:
    """
    A high-level helper that suggests photo/scene settings and preset patches
    for the Dynamic Outfit nodes. It focuses on photography choices: genre,
    vibe, lighting, lens, framing, etc., and returns:

    - positive_additions: a comma-separated prompt fragment to append
    - negative_additions: a comma-separated negative prompt fragment
    - preset_patch_json: JSON string with keys compatible with outfit node inputs
    - guidance_json: JSON metadata of selections
    """

    @classmethod
    def INPUT_TYPES(cls):
        base_dir = Path(__file__).resolve().parents[1]
        data_dir = base_dir / "data"

        # Discover genders and age groups from data
        genders = discover_genders(data_dir / "outfit")
        if not genders:
            genders = ["female", "male"]

        age_groups = load_global_options(data_dir, "age_groups.json", "age_groups")
        if not age_groups:
            age_groups = ["none", "random", "young adult (20-29 years)", "adult (30-39 years)"]

    # Curated lists come from data/styles/photo_helper_options.json
        options = load_json_file(data_dir / "styles" / "photo_helper_options.json", {}) or {}
        outfit_vibes = options.get("outfit_vibes", [])
        photo_genres = options.get("photo_genres", [])
        render_medium = options.get("render_medium", [])
        toon_shading = options.get("toon_shading", [])
        outline_style = options.get("outline_style", [])
        face_proportions = options.get("face_proportions", [])
        frame_type = options.get("frame_type", [])
        character_templates = options.get("character_templates", ["none"])  # for character sheets/turnarounds
        camera_framing = options.get("camera_framing", [])
        lighting_styles = options.get("lighting_styles", [])
        lenses = options.get("lenses", [])
        depth_of_field = options.get("depth_of_field", [])
        aspect_ratios = options.get("aspect_ratios", [])
        palettes = options.get("palettes", [])
        composition = options.get("composition", [])
        quality = options.get("quality", [])

        # Body types: union across available genders
        body_types_union: List[str] = ["none", "random"]
        for g in genders:
            g_types = load_body_types(data_dir / "outfit" / g)
            for t in g_types:
                if t not in body_types_union:
                    body_types_union.append(t)

        # Optional tunables present in JSON (data-driven without further code changes)
        studio_backdrops = options.get("studio_backdrops")
        toon_palettes = options.get("toon_palettes")

        return {
            "required": {
                "gender": (genders, {"default": genders[0], "tooltip": "Target gender for outfit parts"}),
                "age_group": (age_groups, {"default": "random", "tooltip": "Age bracket of the subject"}),
                "body_type": (body_types_union, {"default": "random", "tooltip": "Body type shaping outfit fit"}),
                "outfit_vibe": (outfit_vibes, {"default": "modern", "tooltip": "Overall style vibe"}),
                "photo_genre": (photo_genres, {"default": "portrait", "tooltip": "Photography genre template"}),
                "render_medium": (render_medium, {"default": "photorealistic", "tooltip": "Switch to 2D anime/cartoon/etc."}),
                "toon_shading": (toon_shading, {"default": "auto", "tooltip": "2D shading style"}),
                "outline_style": (outline_style, {"default": "auto", "tooltip": "Lineart / outline emphasis"}),
                "face_proportions": (face_proportions, {"default": "natural", "tooltip": "Face stylization level"}),
                "frame_type": (frame_type, {"default": "photo", "tooltip": "Output framing type"}),
                "character_template": (character_templates, {"default": "none", "tooltip": "Character sheet / turnaround presets"}),
                "camera_framing": (camera_framing, {"default": "waist-up", "tooltip": "How much of the subject is visible"}),
                "lighting": (lighting_styles, {"default": "softbox", "tooltip": "Lighting setup"}),
                "lens": (lenses, {"default": "85mm", "tooltip": "Focal length"}),
                "dof": (depth_of_field, {"default": "shallow", "tooltip": "Depth of field"}),
                "aspect_ratio": (aspect_ratios, {"default": "3:2", "tooltip": "Canvas aspect ratio (hint)"}),
                "palette": (palettes, {"default": "auto", "tooltip": "Color palette intent"}),
                "composition": (composition, {"default": "rule of thirds", "tooltip": "Composition rule"}),
                "quality": (quality, {"default": "studio quality", "tooltip": "Rendering quality keyword"}),
                "description_style": (["random", "sdxl", "flux"], {"default": "random", "tooltip": "Model style profile"}),
                "creative_scale": (["none", "subtle", "balanced", "detailed"], {"default": "balanced", "tooltip": "Creative/detail emphasis"}),
                **({"studio_backdrop": (studio_backdrops, {"default": studio_backdrops[0]})} if isinstance(studio_backdrops, list) and studio_backdrops else {}),
                **({"toon_palette": (toon_palettes, {"default": toon_palettes[0]})} if isinstance(toon_palettes, list) and toon_palettes else {}),
                "quality_preset": (["fast", "balanced", "high"], {"default": "balanced", "tooltip": "Sampler hints for downstream nodes"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "positive_additions",
        "negative_additions",
        "preset_patch_json",
        "guidance_json",
    )
    FUNCTION = "build"
    CATEGORY = "Wizdroid/Outfits/Support"

    def build(self, **kw):
        import json

        gender = kw.get("gender")
        age_group = kw.get("age_group")
        body_type = kw.get("body_type")
        vibe = kw.get("outfit_vibe")
        genre = kw.get("photo_genre")
        medium = kw.get("render_medium")
        shading = kw.get("toon_shading")
        outline = kw.get("outline_style")
        face = kw.get("face_proportions")
        frame = kw.get("frame_type")
        character_template = kw.get("character_template")
        framing = kw.get("camera_framing")
        lighting = kw.get("lighting")
        lens = kw.get("lens")
        dof = kw.get("dof")
        aspect = kw.get("aspect_ratio")
        palette = kw.get("palette")
        studio_backdrop = kw.get("studio_backdrop")
        toon_palette = kw.get("toon_palette")
        composition = kw.get("composition")
        quality = kw.get("quality")
        description_style = kw.get("description_style")
        creative_scale = kw.get("creative_scale")

        # Positive fragment assembly
        pos_parts: List[str] = []

        # Framing and lighting may be less relevant for some 2D media but still helpful
        if frame and frame != "photo":
            pos_parts.append(frame)

        if medium == "photorealistic":
            pos_parts.extend([
                f"{genre} photography",
                f"{framing} composition",
                f"{lighting} lighting",
                f"{lens} lens",
                f"{dof} depth of field",
                f"{quality}",
            ])
        else:
            # 2D / illustrative descriptors
            if isinstance(medium, str) and medium:
                pos_parts.append(medium)
            # Include framing as subject scaling guidance even in 2D
            if framing:
                pos_parts.append(f"{framing}")
            # Stylization toggles
            if shading and shading != "auto":
                pos_parts.append(shading)
            if outline and outline != "auto":
                pos_parts.append(outline)
            if face and face != "natural":
                pos_parts.append(f"{face} facial proportions")
            # Overall quality word still useful
            if quality:
                pos_parts.append(quality)
        if palette and palette != "auto":
            pos_parts.append(palette)
        if composition:
            pos_parts.append(composition)
        if vibe and vibe not in ("none", "random"):
            pos_parts.append(f"{vibe} vibe")

        # Negative fragment heuristics by genre
        neg_parts: List[str] = ["blurry", "low-res"]
        if genre in ("passport",):
            neg_parts.extend(["tilted head", "dramatic lighting", "strong shadows", "open mouth teeth"])
        if genre in ("selfie", "street"):
            neg_parts.append("motion blur")

        # Medium-aware negatives
        if medium and medium != "photorealistic":
            # Avoid realistic skin/details when aiming for 2D
            neg_parts.extend([
                "photorealistic skin", "skin pores", "realistic skin texture", "uncanny valley",
                "specular skin highlights",
            ])
            if medium in ("2D anime", "manga"):
                neg_parts.append("cross-hatched shading")  # nudge away from western comic rendering if anime
        else:
            # If photorealistic, gently avoid cartoonish cues
            neg_parts.extend(["flat shading", "bold outlines", "thick outlines"])

        # Preset patch to feed DynamicOutfitNode
        preset_patch: Dict[str, Any] = {
            "age_group": age_group or "random",
            "body_type": body_type or "random",
            "description_style": description_style or "random",
            "creative_scale": creative_scale or "none",
        }

        # For 2D media, prefer brighter scenes and clean backgrounds by default
        if medium and medium != "photorealistic":
            preset_patch.setdefault("mood", "whimsical" if vibe in ("pinup", "boho") else "bright")
            preset_patch.setdefault("time_of_day", "day")
            if studio_backdrop:
                preset_patch.setdefault("background", studio_backdrop)
            else:
                preset_patch.setdefault("background", "Art gallery")
            if toon_palette:
                preset_patch.setdefault("color_scheme", toon_palette)
            else:
                preset_patch.setdefault("color_scheme", "vibrant" if palette == "auto" else palette)

        # Character sheet / turnaround / sprite sheet templates override some choices
        if character_template and character_template != "none":
            # Neutral, even lighting + plain backgrounds for clarity
            preset_patch.update({
                "mood": "neutral",
                "time_of_day": "studio",
                "background": "Minimalist bedroom",
                "color_scheme": "neutral",
            })
            # Add template hint to custom attributes later via pos_parts
            pos_parts.append(character_template)

        # Suggest mood/time/background based on genre
        if genre in ("fashion", "editorial", "runway"):
            preset_patch.update({
                "mood": "dramatic",
                "time_of_day": "studio",  # not in list but harmless as selector
                "background": "Fashion runway",
                "color_scheme": "vibrant" if palette == "auto" else palette,
            })
        elif genre in ("portrait", "glamour"):
            preset_patch.update({
                "mood": "intimate" if genre == "portrait" else "euphoric",
                "time_of_day": "golden hour",
                "background": "Art gallery",
                "color_scheme": "warm tones" if palette == "auto" else palette,
            })
        elif genre in ("passport",):
            preset_patch.update({
                "mood": "neutral",
                "time_of_day": "midday",
                "background": "Minimalist bedroom",
                "color_scheme": "neutral",
            })
        else:
            preset_patch.update({
                "mood": "serene",
                "time_of_day": "afternoon",
                "background": "Sunny park lawn",
                "color_scheme": "cool tones" if palette == "auto" else palette,
            })

        # Glamour quick filter: bias toward glam scene accents when selected vibe is glamour
        if (vibe or "").lower() == "glamour":
            preset_patch["background"] = preset_patch.get("background", "Luxury hotel lobby")
            if preset_patch.get("background") not in ("Luxury hotel lobby", "Classic ballroom", "Fashion runway"):
                preset_patch["background"] = "Luxury hotel lobby"
            preset_patch["mood"] = "dramatic"
            if palette == "auto":
                preset_patch["color_scheme"] = "vibrant"

        # Compose a custom_attributes string for Outfit node
        custom_attr = ", ".join(pos_parts + [f"aspect ratio {aspect}"])
        preset_patch["custom_attributes"] = custom_attr

        # Minimal guidance metadata and sampler hints
        sampler_hints = {
            "fast": {"steps": 20, "cfg": 4.5, "denoise": 0.5, "resolution": "768x1024"},
            "balanced": {"steps": 30, "cfg": 5.5, "denoise": 0.55, "resolution": "832x1216"},
            "high": {"steps": 40, "cfg": 6.5, "denoise": 0.6, "resolution": "1024x1365"},
        }
        qp = kw.get("quality_preset", "balanced")
        hints = sampler_hints.get(qp, sampler_hints["balanced"]) 

        # Minimal guidance metadata
        guidance = {
            "gender": gender,
            "age_group": age_group,
            "body_type": body_type,
            "vibe": vibe,
            "genre": genre,
            "render_medium": medium,
            "toon_shading": shading,
            "outline_style": outline,
            "face_proportions": face,
            "frame_type": frame,
            "framing": framing,
            "lighting": lighting,
            "lens": lens,
            "depth_of_field": dof,
            "aspect_ratio": aspect,
            "palette": palette,
            "composition": composition,
            "quality": quality,
            "quality_preset": qp,
            "sampler_hints": hints,
        }

        try:
            preset_json = json.dumps(preset_patch, ensure_ascii=False)
            guidance_json = json.dumps(guidance, ensure_ascii=False)
        except Exception:
            preset_json = "{}"
            guidance_json = "{}"

        positive_additions = ", ".join(pos_parts)
        negative_additions = ", ".join(dict.fromkeys(neg_parts))  # dedupe preserve order

        return (
            positive_additions,
            negative_additions,
            preset_json,
            guidance_json,
        )


class ImageValidatorNode:
    """
    Node to validate and fix image tensor shapes before saving.
    Fixes malformed tensors that cause save_images errors.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("validated_image",)
    FUNCTION = "validate_image"
    CATEGORY = "Wizdroid/Outfits/Support"

    def validate_image(self, image):
        """
        Validate and fix image tensor shape.
        Handles cases where tensor has incorrect dimensions.
        """
        try:
            import torch

            # Ensure tensor is on CPU and convert to numpy
            if hasattr(image, 'cpu'):
                img_np = image.cpu().numpy()
            else:
                img_np = image

            # Handle different tensor shapes
            if img_np.ndim == 4:  # (batch, height, width, channels)
                batch_size, height, width, channels = img_np.shape

                # Fix malformed shapes
                if height == 1 and width > 1:
                    # If height is 1 but width is normal, this might be a 1D tensor incorrectly shaped
                    print(f"[ImageValidator] Detected malformed tensor shape: {img_np.shape}")
                    # Try to reshape to a square image
                    total_pixels = height * width * channels
                    if total_pixels >= 512 * 512 * 3:  # Minimum size for 512x512 RGB
                        # Reshape to approximate square
                        side = int((total_pixels / 3) ** 0.5)
                        if side >= 64:  # Minimum reasonable size
                            img_np = img_np.reshape(batch_size, side, side, channels)
                            print(f"[ImageValidator] Reshaped to: {img_np.shape}")
                        else:
                            # Fallback: create a small valid image
                            img_np = img_np.reshape(batch_size, 64, 64, channels)
                            print(f"[ImageValidator] Fallback reshaped to: {img_np.shape}")
                    else:
                        # Create a minimal valid image
                        img_np = img_np.reshape(batch_size, 64, 64, channels)
                        print(f"[ImageValidator] Created minimal valid shape: {img_np.shape}")

                # Ensure values are in valid range
                img_np = img_np.clip(0, 1)

            elif img_np.ndim == 3:  # (height, width, channels)
                height, width, channels = img_np.shape

                # Handle single image case
                if height == 1 and width > 1:
                    print(f"[ImageValidator] Detected malformed single image shape: {img_np.shape}")
                    # Try to fix similar to batch case
                    total_pixels = height * width * channels
                    if total_pixels >= 512 * 512 * 3:
                        side = int((total_pixels / 3) ** 0.5)
                        if side >= 64:
                            img_np = img_np.reshape(side, side, channels)
                        else:
                            img_np = img_np.reshape(64, 64, channels)
                    else:
                        img_np = img_np.reshape(64, 64, channels)

                    print(f"[ImageValidator] Fixed to: {img_np.shape}")

                # Add batch dimension if missing
                img_np = img_np.unsqueeze(0) if hasattr(img_np, 'unsqueeze') else img_np[None, ...]

            # Convert back to torch tensor if needed
            if hasattr(image, 'device'):
                import torch
                img_tensor = torch.from_numpy(img_np).to(image.device)
            else:
                img_tensor = img_np

            return (img_tensor,)

        except Exception as e:
            print(f"[ImageValidator] Error validating image: {e}")
            # Return a minimal valid image as fallback
            import torch
            fallback = torch.zeros(1, 64, 64, 3)
            return (fallback,)


# Node registration
NODE_CLASS_MAPPINGS = {
    "PhotoStyleHelperNode": PhotoStyleHelperNode,
    "ImageValidatorNode": ImageValidatorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PhotoStyleHelperNode": "🎨 Photo Style Helper",
    "ImageValidatorNode": "🔧 Image Validator",
}
