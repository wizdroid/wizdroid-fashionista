import json
import random
from typing import Any, Dict, List
from pathlib import Path

from .common import safe_random_choice, compose_negative_prompt, clean_comma_separated_terms

MODEL_STYLE_HINTS = {
    "sdxl": {
        "prefer_weights": True,
        "extra": "high detail, coherent composition",
    },
    "flux": {
        "prefer_weights": False,
        "extra": "natural language style, coherent narrative phrasing",
    },
    "sd3": {
        "prefer_weights": False,
        "extra": "simple concise tags, avoid heavy weighting syntax",
    },
}

def _load_description_styles() -> Dict[str, Dict[str, str]]:
    """Load data/styles/description_prompts.json for richer model-aware hints.
    Fallback to empty dict if not present or unreadable.
    """
    try:
        base_dir = Path(__file__).resolve().parents[1]
        file_path = base_dir / "data" / "styles" / "description_prompts.json"
        import json as _json
        with open(file_path, "r", encoding="utf-8") as f:
            data = _json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

_NEG_BASELINE: List[str] = []

def _load_negative_baseline() -> List[str]:
    global _NEG_BASELINE
    if _NEG_BASELINE:
        return _NEG_BASELINE
    try:
        base_dir = Path(__file__).resolve().parents[1]
        file_path = base_dir / "data" / "styles" / "negative_baseline.json"
        import json as _json
        with open(file_path, "r", encoding="utf-8") as f:
            data = _json.load(f)
            vals = data.get("negatives", []) if isinstance(data, dict) else []
            if isinstance(vals, list):
                _NEG_BASELINE = [str(v) for v in vals if isinstance(v, str)]
                return _NEG_BASELINE
    except Exception:
        pass
    _NEG_BASELINE = []
    return _NEG_BASELINE

class PromptBuilder:
    def __init__(self, seed: int, data: Dict[str, Any], options: Dict[str, List[str]]):
        self.seed = seed
        self.data = data
        self.options = options
        self.prompt_parts = []
        self._auto_negative_terms: List[str] = []
        self._metadata: Dict[str, Any] = {"seed": seed, "selections": {}, "auto_negatives": []}
        random.seed(self.seed)

    def _add_part(self, key: str, label: str, is_random_allowed: bool = True):
        value = self.data.get(key, "none")
        if value == "none":
            return

        if value == "random" and is_random_allowed:
            valid_options = self.options.get(key, [])
            value = safe_random_choice(valid_options)
        
        if value and value != "none":
            self.prompt_parts.append(f"{label}: {value}")
            self._metadata["selections"][key] = value

    def _process_attire(self, body_parts: List[str]):
        attire_parts = []
        for part in body_parts:
            if part == "makeup":
                continue

            value = self.data.get(part, "none")
            if value == "random":
                options = self.options.get(part, [])
                selected = safe_random_choice(options)
                if selected != "none":
                    attire_parts.append(f"{part}: {selected}")
                    self._metadata["selections"][part] = selected
            elif value != "none":
                attire_parts.append(f"{part}: {value}")
                self._metadata["selections"][part] = value
        
        if attire_parts:
            self.prompt_parts.append("Attire: " + ", ".join(attire_parts))

    def _process_makeup(self):
        makeup_parts = []
        makeup_data = self.data.get("makeup_data", "")
        if not makeup_data:
            return

        try:
            makeup_items = json.loads(makeup_data)
            for item in makeup_items:
                if not item.get("enabled", True) or item.get("type") == "none":
                    continue
                
                makeup_type = item.get("type")
                intensity = item.get("intensity", "medium")
                color = item.get("color", "none")

                if color and color != "none":
                    makeup_parts.append(f"{makeup_type} ({color}, {intensity})")
                else:
                    makeup_parts.append(f"{makeup_type} ({intensity})")
        except (json.JSONDecodeError, TypeError) as e:
            print(f"[OutfitNode] Error parsing makeup data: {e}")

        if makeup_parts:
            self.prompt_parts.append("Makeup: " + ", ".join(makeup_parts))
            self._metadata["selections"]["makeup"] = makeup_parts

    def _collect_auto_negative_terms(self):
        """
        Generate a small set of automatic negative prompt terms based on simple conflicts.
        This remains conservative to avoid changing current behavior too much.
        """
        sel = self._metadata.get("selections", {})
        negatives: List[str] = list(_load_negative_baseline())

        # Facial hair vs clean shaven
        facial = sel.get("facial_hair")
        if isinstance(facial, str) and facial:
            if facial == "clean shaven":
                negatives.extend(["beard", "mustache", "goatee", "stubble"])
            else:
                negatives.append("clean shaven")

        # Hairstyle vs shaved head/bald
        hair = sel.get("hairstyle")
        if isinstance(hair, str) and hair:
            if hair in ("shaved head", "buzz cut"):
                negatives.extend(["long hair", "ponytail", "braid", "bun"])
            else:
                negatives.extend(["bald", "shaved head"])  # avoid unintended bald look

        # Eyewear explicit none
        eyewear = sel.get("eyewear")
        if isinstance(eyewear, str) and eyewear:
            if eyewear == "no eyewear":
                negatives.extend(["glasses", "sunglasses", "goggles", "monocle"])  # generic blockers

    # Basic cleanliness already seeded from baseline; keep list minimal here

        # Dedup and clean
        cleaned = clean_comma_separated_terms(", ".join(negatives))
        self._auto_negative_terms = [t.strip() for t in cleaned.split(", ") if t.strip()]
        self._metadata["auto_negatives"] = list(self._auto_negative_terms)

    def build(self, body_parts: List[str]) -> str:
        character_name = self.data.get("character_name", "").strip()
        if character_name:
            self.prompt_parts.append(f"Character: {character_name}")
            self._metadata["selections"]["character_name"] = character_name

        self._add_part("age_group", "Age")
        self._add_part("race", "Race")
        self._add_part("body_type", "Body type")

        self._process_attire(body_parts)
        self._process_makeup()

        self._add_part("pose", "Pose")
        self._add_part("background", "Background")

        # Scene/style controls
        self._add_part("mood", "Mood")
        self._add_part("time_of_day", "Time")
        self._add_part("weather", "Weather")
        self._add_part("color_scheme", "Color scheme")
        # These are selectors; the actual mapping to instruction text can be handled downstream
        self._add_part("description_style", "Style")
        self._add_part("creative_scale", "Scale")

        # Add model-aware style hint using local data/styles/description_prompts.json
        model_key = (self.data.get("description_style") or "").strip().lower()
        styles_data = _load_description_styles()
        if model_key in styles_data:
            # include a short hint based on instructions without bloating output
            instr = styles_data[model_key].get("instructions") or ""
            if instr:
                short = instr.split(".")[0].strip()  # first sentence as a short guidance
                if short:
                    self.prompt_parts.append(f"Model hint: {short}")
        elif model_key in MODEL_STYLE_HINTS:
            hint = MODEL_STYLE_HINTS[model_key].get("extra")
            if hint:
                self.prompt_parts.append(f"Model hint: {hint}")

        custom_attributes = self.data.get("custom_attributes", "").strip()
        if custom_attributes:
            self.prompt_parts.append(f"Additional: {custom_attributes}")
            self._metadata["selections"]["custom_attributes"] = custom_attributes

        # Negative/avoid terms
        # Compose negative prompt (user terms + auto)
        self._collect_auto_negative_terms()
        avoid_terms = compose_negative_prompt(self.data.get("avoid_terms", ""), self._auto_negative_terms)
        avoid_terms = avoid_terms.strip()
        if avoid_terms:
            self.prompt_parts.append(f"Avoid: {avoid_terms}")
            self._metadata["negative_prompt"] = avoid_terms

        return ", ".join(self.prompt_parts)

    def get_negative_prompt(self) -> str:
        """Return the composed negative prompt computed during build()."""
        return self._metadata.get("negative_prompt", "")

    def get_metadata(self) -> Dict[str, Any]:
        """Return metadata about selections, auto negatives, and seed."""
        return dict(self._metadata)
