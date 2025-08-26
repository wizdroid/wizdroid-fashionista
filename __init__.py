"""Top-level package initializer for comfyui-outfit.

This file is imported by ComfyUI as a plugin package. It may also be imported
directly by tooling (e.g., pytest collection). To be robust in both contexts,
we attempt a normal relative import first and fall back to a file-based import
when no package context is available.
"""

# Tell ComfyUI where to find our web assets
WEB_DIRECTORY = "web"

import os

# If running under pytest collection, avoid importing heavy plugin modules.
if os.environ.get("PYTEST_CURRENT_TEST"):
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}
    print("ComfyUI Outfit: Skipping node import during pytest collection")
else:
    # Import main nodes (robust to both package and direct import contexts)
    try:
        from .dynamic_outfit_node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS  # type: ignore
    except Exception as e:  # pragma: no cover - only used in non-package contexts
        # Fallback: synthesize a package so relative imports work, then import by file path
        import sys
        import types
        import importlib.util
        from pathlib import Path

        base_dir = Path(__file__).parent
        pkg_name = "comfyui_outfit"

        if pkg_name not in sys.modules:
            pkg = types.ModuleType(pkg_name)
            pkg.__path__ = [str(base_dir)]  # mark as package
            sys.modules[pkg_name] = pkg

        dyn_path = base_dir / "dynamic_outfit_node.py"
        spec = importlib.util.spec_from_file_location(f"{pkg_name}.dynamic_outfit_node", str(dyn_path))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[f"{pkg_name}.dynamic_outfit_node"] = mod
            spec.loader.exec_module(mod)
            NODE_CLASS_MAPPINGS = getattr(mod, "NODE_CLASS_MAPPINGS", {})
            NODE_DISPLAY_NAME_MAPPINGS = getattr(mod, "NODE_DISPLAY_NAME_MAPPINGS", {})
            print("ComfyUI Outfit: Loaded nodes via fallback import mechanism")
        else:  # If loader could not be created, re-raise the original error
            raise

# Attempt to import optional support nodes
try:
    if not os.environ.get("PYTEST_CURRENT_TEST"):
        try:
            from .support_nodes import (  # type: ignore
                SUPPORT_NODE_CLASS_MAPPINGS,
                SUPPORT_NODE_DISPLAY_NAME_MAPPINGS,
            )
        except Exception:
            # Fallback path-based import for support nodes as well
            import sys
            import types
            import importlib.util
            from pathlib import Path

            base_dir = Path(__file__).parent
            pkg_name = "comfyui_outfit"
            if pkg_name not in sys.modules:
                pkg = types.ModuleType(pkg_name)
                pkg.__path__ = [str(base_dir)]
                sys.modules[pkg_name] = pkg

            supp_init = base_dir / "support_nodes" / "__init__.py"
            spec = importlib.util.spec_from_file_location(
                f"{pkg_name}.support_nodes", str(supp_init)
            )
            if spec and spec.loader:
                supp_mod = importlib.util.module_from_spec(spec)
                sys.modules[f"{pkg_name}.support_nodes"] = supp_mod
                spec.loader.exec_module(supp_mod)
                SUPPORT_NODE_CLASS_MAPPINGS = getattr(supp_mod, "SUPPORT_NODE_CLASS_MAPPINGS", {})
                SUPPORT_NODE_DISPLAY_NAME_MAPPINGS = getattr(supp_mod, "SUPPORT_NODE_DISPLAY_NAME_MAPPINGS", {})
            else:
                raise ImportError("Failed to load support_nodes module")

        # Merge the mappings if present
        if SUPPORT_NODE_CLASS_MAPPINGS:
            NODE_CLASS_MAPPINGS.update(SUPPORT_NODE_CLASS_MAPPINGS)
        if SUPPORT_NODE_DISPLAY_NAME_MAPPINGS:
            NODE_DISPLAY_NAME_MAPPINGS.update(SUPPORT_NODE_DISPLAY_NAME_MAPPINGS)

        print("ComfyUI Outfit: Successfully loaded support nodes (Ollama Vision & LLM)")
except Exception as e:
    # Keep optional; print and continue
    print(f"ComfyUI Outfit: Support nodes not available (missing dependencies): {e}")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
