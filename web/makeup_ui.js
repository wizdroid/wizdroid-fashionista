// Dynamic Makeup Widget for ComfyUI Outfit Node
import { app } from "../../scripts/app.js";

console.log("ComfyUI Outfit Dynamic Makeup UI - Starting to load...");

console.log("Loading ComfyUI Outfit Dynamic Makeup UI...");

app.registerExtension({
    name: "comfyui.outfit.makeup",
    
    init() {
        console.log("ComfyUI Outfit extension initialized!");
    },
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        console.log("Checking node for makeup support:", nodeData.name);
        
        if (nodeData.name === "FemaleOutfitNode" || nodeData.name === "MaleOutfitNode") {
            console.log(`*** FOUND ${nodeData.name}! Adding makeup functionality...`);
            
            // --- Dynamic Makeup System ---
            nodeType.prototype.addMakeupSystem = function() {
                console.log("Adding makeup system to node");
                
                this.makeupWidgets = [];
                this.makeupCounter = 0;
                
                // Add hidden input to store makeup data
                this.makeupDataWidget = this.addWidget("string", "makeup_data", "", null, {
                    multiline: false,
                    serialize: true
                });
                // Hide the makeup data widget
                this.makeupDataWidget.type = "hidden";
                
                // Add the "Add Makeup" button
                const addButton = this.addWidget("button", "💄 Add Makeup", null, () => {
                    console.log("Add Makeup button clicked!");
                    this.addMakeupItem();
                });
                addButton.serialize = false;
                
                console.log("Makeup system added successfully");
            };
            
            // Add method to serialize makeup data
            nodeType.prototype.serializeMakeupData = function() {
                const makeupData = [];
                
                if (this.makeupWidgets) {
                    this.makeupWidgets.forEach(widget => {
                        if (widget.enabled.value && widget.type.value && widget.type.value !== "none") {
                            makeupData.push({
                                type: widget.type.value,
                                intensity: widget.intensity.value,
                                color: widget.color.value,
                                enabled: widget.enabled.value
                            });
                        }
                    });
                }
                
                const serialized = JSON.stringify(makeupData);
                if (this.makeupDataWidget) {
                    this.makeupDataWidget.value = serialized;
                }
                
                console.log("Serialized makeup data:", serialized);
                return serialized;
            };
            
            // Add method to load makeup data from backend
            nodeType.prototype.loadMakeupData = async function() {
                try {
                    // Load makeup types from backend JSON
                    const genderFolder = this.constructor.name === "FemaleOutfitNode" ? "female" : "male";
                    const makeupResponse = await fetch(`/custom_nodes/comfyui-outfit/data/outfit/${genderFolder}/makeup.json`);
                    const makeupData = await makeupResponse.json();
                    const makeupTypes = ["none", ...makeupData.attire.map(item => item.type)];
                    
                    // Load UI options
                    const uiResponse = await fetch(`/custom_nodes/comfyui-outfit/data/makeup.json`);
                    const uiData = await uiResponse.json();
                    
                    return {
                        makeupTypes,
                        colors: uiData.makeup_colors,
                        intensities: uiData.makeup_intensities
                    };
                } catch (error) {
                    console.error("Error loading makeup data:", error);
                    // Fallback to hardcoded values
                    return {
                        makeupTypes: [
                            "none", "foundation", "concealer", "blush", "lipstick", "lip gloss", "lip stain",
                            "eyeshadow", "eyeliner", "mascara", "eyebrow pencil", "eyebrow gel",
                            "highlighter", "contour", "bronzer", "setting powder", "setting spray", "no makeup"
                        ],
                        colors: [
                            "none", "red", "pink", "peach", "nude", "berry", "coral", "rose", "brown", "black", "clear", 
                            "gold", "silver", "bronze", "taupe", "smoky", "colorful", "white", "purple", "blue", "green", 
                            "yellow", "orange", "maroon", "magenta", "cyan", "lime", "navy", "olive", "teal", "gray", 
                            "light", "medium", "dark", "deep", "bright", "matte", "glossy", "metallic", "shimmer", 
                            "natural", "warm", "cool", "neutral", "transparent", "opaque", "sheer"
                        ],
                        intensities: ["none", "light", "medium", "heavy"]
                    };
                }
            };
            
            // Add method to create individual makeup items
            nodeType.prototype.addMakeupItem = async function() {
                console.log("Adding makeup item");
                
                this.makeupCounter++;
                const widgetName = `makeup_${this.makeupCounter}`;
                
                // Load makeup data from backend
                const makeupData = await this.loadMakeupData();
                
                // Create makeup type dropdown
                const typeWidget = this.addWidget("combo", `${widgetName}_type`, "none", 
                    (value) => { 
                        console.log(`Makeup type changed: ${value}`);
                        this.serializeMakeupData();
                    }, 
                    { values: makeupData.makeupTypes, serialize: false }
                );

                // Create intensity dropdown
                const intensityWidget = this.addWidget("combo", `${widgetName}_intensity`, "medium", 
                    (value) => { 
                        console.log(`Intensity changed: ${value}`);
                        this.serializeMakeupData();
                    }, 
                    { values: makeupData.intensities, serialize: false }
                );

                // Create color dropdown
                const colorWidget = this.addWidget("combo", `${widgetName}_color`, "none",
                    (value) => { this.serializeMakeupData(); },
                    { values: makeupData.colors, serialize: false }
                );

                // Create enabled toggle
                const enabledWidget = this.addWidget("toggle", `${widgetName}_enabled`, true, 
                    (value) => { 
                        console.log(`Enabled changed: ${value}`);
                        this.updateMakeupVisuals(widgetName);
                        this.serializeMakeupData();
                    }, 
                    { serialize: false }
                );

                // Create remove button
                const removeButton = this.addWidget("button", "🗑️ Remove", null, () => {
                    console.log(`Removing makeup item: ${widgetName}`);
                    this.removeMakeupItem(widgetName);
                }, { serialize: false });

                // Store widget references
                const widgetGroup = {
                    name: widgetName,
                    type: typeWidget,
                    intensity: intensityWidget,
                    color: colorWidget,
                    enabled: enabledWidget,
                    remove: removeButton
                };

                this.makeupWidgets.push(widgetGroup);
                this.setSize(this.computeSize());
                
                // Update serialized data
                this.serializeMakeupData();
                
                console.log(`Added makeup item: ${widgetName}`);
            };
            
            // Add method to remove makeup items
            nodeType.prototype.removeMakeupItem = function(widgetName) {
                console.log(`Attempting to remove makeup item: ${widgetName}`);
                
                if (!this.makeupWidgets) {
                    console.log("No makeup widgets found");
                    return;
                }
                
                const widgetIndex = this.makeupWidgets.findIndex(w => w.name === widgetName);
                if (widgetIndex === -1) {
                    console.log(`Widget ${widgetName} not found in makeupWidgets`);
                    return;
                }

                const widgetGroup = this.makeupWidgets[widgetIndex];
                console.log(`Found widget group for ${widgetName}:`, widgetGroup);
                
                // Remove widgets from node - need to find them in the widgets array
                const widgetsToRemove = [
                    widgetGroup.type,
                    widgetGroup.intensity,
                    widgetGroup.color,
                    widgetGroup.enabled,
                    widgetGroup.remove
                ];
                
                widgetsToRemove.forEach(widget => {
                    if (widget && this.widgets) {
                        const index = this.widgets.indexOf(widget);
                        if (index !== -1) {
                            this.widgets.splice(index, 1);
                            console.log(`Removed widget from node widgets array`);
                        }
                    }
                });
                
                // Remove from our tracking
                this.makeupWidgets.splice(widgetIndex, 1);
                
                // Trigger node update
                this.setSize(this.computeSize());
                this.setDirtyCanvas(true);
                
                // Update serialized data
                this.serializeMakeupData();
                
                console.log(`Successfully removed makeup item: ${widgetName}`);
            };
            
            // Add method to update visual styles
            nodeType.prototype.updateMakeupVisuals = function(widgetName) {
                // This could be enhanced to change visual styling based on enabled state
                console.log(`Updating visuals for: ${widgetName}`);
            };
            
            // Call the makeup system in onNodeCreated
            const origOnNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = origOnNodeCreated?.apply(this, arguments);
                this.addMakeupSystem();
                return result;
            };
        }
    }
});

console.log("ComfyUI Outfit Dynamic Makeup UI loaded successfully!");

// NOTE: Nail makeup types (e.g., nail polish, gel nails, acrylic nails, etc.) are included in the backend JSON (makeup.json) and will automatically appear in the UI dropdown if present. No hardcoding needed.
