import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";

// Function to apply styles to an element
function applyStyles(element, styles) {
    for (const key in styles) {
        element.style[key] = styles[key];
    }
}

// Function to create a styled button
function createStyledButton(text, styles) {
    const button = document.createElement("button");
    button.textContent = text;
    applyStyles(button, {
        padding: "8px 12px",
        borderRadius: "4px",
        border: "1px solid #ccc",
        backgroundColor: "#f0f0f0",
        cursor: "pointer",
        ...styles,
    });
    return button;
}

app.registerExtension({
    name: "comfyui.outfit.beautiful_ui",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name.includes("OutfitNode")) {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);

                // Add a styled button to the node
                const button = createStyledButton("✨ Enhance", {
                    position: "absolute",
                    top: "10px",
                    right: "10px",
                    backgroundColor: "#6a5acd",
                    color: "white",
                });

                button.onclick = () => {
                    alert("UI Enhanced!");
                };

                this.addDOMWidget("enhance_button", "button", button);
            };
        }
    },
});
