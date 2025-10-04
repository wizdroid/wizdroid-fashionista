"""Top-level package initializer for wizdroid-outfit.

This file is imported by ComfyUI as a plugin package. It may also be imported
directly by tooling (e.g., pytest collection). To be robust in both contexts,
we attempt a normal relative import first and fall back to a file-based import
when no package context is available.
"""

# Tell ComfyUI where to find our web assets
WEB_DIRECTORY = "web"

import logging
import os

from .nodes.dynamic_outfit import (
    NODE_CLASS_MAPPINGS as dynamic_outfit_mappings,
    NODE_DISPLAY_NAME_MAPPINGS as dynamic_outfit_display_mappings,
)
from .nodes.preset_outfit_node import (
    NODE_CLASS_MAPPINGS as preset_outfit_mappings,
    NODE_DISPLAY_NAME_MAPPINGS as preset_outfit_display_mappings,
)
from .nodes.facial_expression_node import (
    NODE_CLASS_MAPPINGS as facial_expression_mappings,
    NODE_DISPLAY_NAME_MAPPINGS as facial_expression_display_mappings,
)
from .support_nodes import SUPPORT_NODE_CLASS_MAPPINGS, SUPPORT_NODE_DISPLAY_NAME_MAPPINGS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize mappings
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Load main nodes
if dynamic_outfit_mappings and dynamic_outfit_display_mappings:
    NODE_CLASS_MAPPINGS.update(dynamic_outfit_mappings)
    NODE_DISPLAY_NAME_MAPPINGS.update(dynamic_outfit_display_mappings)
    logger.info("ComfyUI Outfit: Loaded dynamic outfit nodes")

if preset_outfit_mappings and preset_outfit_display_mappings:
    NODE_CLASS_MAPPINGS.update(preset_outfit_mappings)
    NODE_DISPLAY_NAME_MAPPINGS.update(preset_outfit_display_mappings)
    logger.info("ComfyUI Outfit: Loaded preset outfit nodes")

if facial_expression_mappings and facial_expression_display_mappings:
    NODE_CLASS_MAPPINGS.update(facial_expression_mappings)
    NODE_DISPLAY_NAME_MAPPINGS.update(facial_expression_display_mappings)
    logger.info("ComfyUI Outfit: Loaded facial expression nodes")

# Load support nodes
if SUPPORT_NODE_CLASS_MAPPINGS and SUPPORT_NODE_DISPLAY_NAME_MAPPINGS:
    NODE_CLASS_MAPPINGS.update(SUPPORT_NODE_CLASS_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(SUPPORT_NODE_DISPLAY_NAME_MAPPINGS)
    logger.info("ComfyUI Outfit: Loaded support nodes")

# Handle pytest environment
if os.environ.get("PYTEST_CURRENT_TEST"):
    NODE_CLASS_MAPPINGS.clear()
    NODE_DISPLAY_NAME_MAPPINGS.clear()
    logger.info("ComfyUI Outfit: Skipping node import during pytest collection")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
