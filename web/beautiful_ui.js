import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";

// Minimal extension for ComfyUI Outfit nodes
app.registerExtension({
    name: "comfyui.outfit.ui",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // This extension can be used for future UI enhancements
        // Currently disabled to avoid interfering with user experience
    },
});
