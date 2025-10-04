from __future__ import annotations

import json
from typing import Any, Dict


class PresetPatchApplierNode:
    """
    Applies a preset_patch_json (from the Photo Style Helper) to an existing
    mapping of Outfit node inputs and returns a merged JSON mapping.

    Inputs:
      - preset_patch_json: JSON string (dict of key->value)
      - existing_json: optional JSON string representing current inputs

    Output:
      - merged_json: JSON string suitable for feeding into a downstream node
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset_patch_json": ("STRING", {"multiline": True, "default": "{}"}),
                "existing_json": ("STRING", {"multiline": True, "default": "{}"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("patched_json",)
    FUNCTION = "apply_patch"
    CATEGORY = "Wizdroid/Utils/Data"

    def apply(self, preset_patch_json: str, existing_json: str = "{}"):
        def _parse(s: str) -> Dict[str, Any]:
            try:
                obj = json.loads(s or "{}")
                return obj if isinstance(obj, dict) else {}
            except Exception:
                return {}

        base = _parse(existing_json)
        patch = _parse(preset_patch_json)

        # Shallow merge: patch overrides base where provided and non-empty
        merged = dict(base)
        for k, v in patch.items():
            if isinstance(v, str) and v.strip() == "":
                continue
            merged[k] = v

        try:
            out = json.dumps(merged, ensure_ascii=False)
        except Exception:
            out = "{}"
        return (out,)
