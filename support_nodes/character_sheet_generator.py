"""
Character Sheet Generator Node for ComfyUI Outfit Selection.
Generates detailed prompts for creating character sheets, turnarounds, and expression studies.
"""

from typing import List, Tuple

class CharacterSheetGeneratorNode:
    """
    A node to generate prompts for character sheets, including multiple views,
    expressions, and poses.
    """

    @classmethod
    def INPUT_TYPES(cls):
        """Define input fields for the ComfyUI node."""
        sheet_styles = [
            "character turnaround",
            "expression sheet",
            "action pose sheet",
            "outfit sheet",
            "anatomy study",
            "sprite sheet",
        ]
        
        view_options = [
            "none",
            "front, side, back",
            "front, 3/4, side, back",
            "multiple angles",
            "dynamic angles",
            "full turn",
        ]

        expression_options = [
            "none",
            "neutral, happy, sad, angry",
            "happy, surprised, angry, sad, disgusted, fearful",
            "subtle expressions",
            "dynamic expressions",
            "comedic expressions",
        ]

        layout_options = [
            "grid layout",
            "row layout",
            "dynamic composition",
            "t-pose, a-pose",
        ]

        background_options = [
            "plain white background",
            "light gray background",
            "transparent background",
            "blueprint grid background",
            "gradient background",
            "no background",
        ]

        annotation_options = [
            "none",
            "text labels for views",
            "arrows and callouts",
            "color palette swatches",
            "detailed annotations",
        ]

        return {
            "required": {
                "character_prompt": ("STRING", {"multiline": True, "default": "1girl, solo, brown hair, green eyes, wearing a red jacket and blue jeans"}),
                "sheet_style": (sheet_styles, {"default": "character turnaround"}),
                "views": (view_options, {"default": "front, side, back"}),
                "expressions": (expression_options, {"default": "none"}),
                "layout": (layout_options, {"default": "grid layout"}),
                "background": (background_options, {"default": "plain white background"}),
                "annotations": (annotation_options, {"default": "text labels for views"}),
                "art_style": ("STRING", {"multiline": False, "default": "concept art, detailed, high quality"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("character_sheet_prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "Wizdroid/Utils/Character"

    def generate_prompt(
        self,
        character_prompt: str,
        sheet_style: str,
        views: str,
        expressions: str,
        layout: str,
        background: str,
        annotations: str,
        art_style: str,
    ) -> Tuple[str]:
        """
        Generates a detailed prompt for a character sheet.
        """
        prompt_parts: List[str] = []
        base_char = f"({character_prompt.strip()})"
        
        if sheet_style == "character turnaround":
            prompt_parts.append(f"character sheet, {base_char}, full body, standing")
            views = "front, side, back" if views == "none" else views
            prompt_parts.append(f"multiple views: ({views})")
            if "t-pose" not in layout and "a-pose" not in layout:
                layout = "t-pose, a-pose"
        elif sheet_style == "expression sheet":
            prompt_parts.append(f"expression sheet, {base_char}, portrait, bust shot")
            expressions = "neutral, happy, sad, angry" if expressions == "none" else expressions
            prompt_parts.append(f"multiple expressions: ({expressions})")
        elif sheet_style == "action pose sheet":
            prompt_parts.append(f"action pose sheet, {base_char}, dynamic poses, full body, various action poses: (running, jumping, fighting, crouching)")
        elif sheet_style == "outfit sheet":
            prompt_parts.append(f"outfit sheet, {base_char}, showing different clothes, multiple outfits: (casual wear, formal wear, fantasy armor)")
        else:
            prompt_parts.append(f"{sheet_style}, {base_char}")
            if views != "none": prompt_parts.append(f"multiple views: ({views})")
            if expressions != "none": prompt_parts.append(f"multiple expressions: ({expressions})")

        prompt_parts.extend([layout, background])
        if annotations != "none": prompt_parts.append(annotations)
        if art_style.strip(): prompt_parts.append(art_style.strip())

        final_prompt = ", ".join(filter(None, prompt_parts))
        final_prompt += ", same character, consistent character, character design, masterpiece"

        print(f"[CharacterSheetGenerator] Generated prompt: {final_prompt}")
        
        return (final_prompt,)