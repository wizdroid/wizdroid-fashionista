import { app } from "/scripts/app.js";

const MakeupAPI = {
    _cache: {},
    async _fetchJSON(path) {
        const key = `json:${path}`;
        if (this._cache[key]) return this._cache[key];
        const res = await fetch(path);
        if (!res.ok) throw new Error(`${path}: ${res.status} ${res.statusText}`);
        const data = await res.json();
        this._cache[key] = data;
        return data;
    },
    async getUiOptions() {
        try {
            const data = await this._fetchJSON(`/custom_nodes/comfyui-outfit/data/ui_options.json`);
            console.log("[ComfyUI-Outfit] Loaded UI options:", data);
            
            // Ensure we have the makeup_colors array
            if (!data || !Array.isArray(data.makeup_colors)) {
                console.warn("[ComfyUI-Outfit] makeup_colors not found, using fallback");
                return { 
                    colors: ["none", "red", "pink", "peach", "nude", "berry", "coral", "rose", "brown", "black", "clear", "gold", "silver", "bronze", "taupe", "smoky", "colorful", "white", "purple", "blue", "green", "yellow", "orange", "maroon", "magenta", "cyan", "lime", "navy", "olive", "teal", "gray", "light", "medium", "dark", "deep", "bright", "matte", "glossy", "metallic", "shimmer", "natural", "warm", "cool", "neutral", "transparent", "opaque", "sheer"], 
                    intensities: ["none", "light", "medium", "heavy"] 
                };
            }
            
            const colors = ["none", ...data.makeup_colors];
            const intensities = ["none", ...(data.makeup_intensities || ["light", "medium", "heavy"])];
            console.log("[ComfyUI-Outfit] Final colors:", colors.length, "items");
            return { colors, intensities };
        } catch (e) {
            console.warn("[ComfyUI-Outfit] Using fallback UI options due to error:", e);
            return { 
                colors: ["none", "red", "pink", "peach", "nude", "berry", "coral", "rose", "brown", "black", "clear", "gold", "silver", "bronze", "taupe", "smoky", "colorful", "white", "purple", "blue", "green", "yellow", "orange", "maroon", "magenta", "cyan", "lime", "navy", "olive", "teal", "gray", "light", "medium", "dark", "deep", "bright", "matte", "glossy", "metallic", "shimmer", "natural", "warm", "cool", "neutral", "transparent", "opaque", "sheer"], 
                intensities: ["none", "light", "medium", "heavy"] 
            };
        }
    },
    async getMakeupData(gender) {
        try {
            const [ui, typesData] = await Promise.all([
                this.getUiOptions(),
                this._fetchJSON(`/custom_nodes/comfyui-outfit/data/outfit/${gender}/makeup.json`),
            ]);
            const types = ["none", ...(typesData.attire?.map(item => item.type) || [])];
            return { types, colors: ui.colors, intensities: ui.intensities };
        } catch (error) {
            console.error("[ComfyUI-Outfit] Error loading makeup data:", error);
            return {
                types: ["none", "lipstick", "eyeshadow", "blush"],
                colors: ["none", "red", "pink", "nude"],
                intensities: ["none", "light", "medium", "heavy"],
            };
        }
    },
};

class MakeupItem {
    constructor(node, id, makeupData, onRemove, onDuplicate) {
        this.node = node;
        this.id = id;
        this.makeupData = makeupData;
        this.onRemove = onRemove;
        this.onDuplicate = onDuplicate;
        this.createdAt = performance.now();
        this.widget = this.createWidget();
    }

    createWidget() {
        const widget = {
            type: "div",
            name: `makeup_item_${this.id}`,
            draw: (ctx, node, widgetWidth, y, widgetHeight) => {
                // Draw rounded background with subtle animated sheen on creation
                const elapsed = (performance.now() - this.createdAt) / 1000;
                const pulse = Math.max(0, 1.0 - Math.min(elapsed / 1.2, 1)); // fade in ~1.2s
                const x = node.pos[0] + 10;
                const w = Math.max(180, widgetWidth - 20);
                const h = Math.max(28, (this.widget?.widgets?.length || 1) * 22 + 8);
                const r = 8;
                ctx.save();
                ctx.globalAlpha = 0.8;
                ctx.fillStyle = "#1f2937"; // slate-800
                ctx.strokeStyle = `rgba(59,130,246,${0.6 + 0.3 * pulse})`; // blue-500 with pulse
                ctx.lineWidth = 1.5 + 1.0 * pulse;
                const px = 6, py = y - 2;
                if (ctx.roundRect) {
                    ctx.beginPath();
                    ctx.roundRect(px, py, w, h, r);
                    ctx.fill();
                    ctx.stroke();
                } else {
                    // Fallback rounded box
                    ctx.beginPath();
                    ctx.moveTo(px + r, py);
                    ctx.arcTo(px + w, py, px + w, py + h, r);
                    ctx.arcTo(px + w, py + h, px, py + h, r);
                    ctx.arcTo(px, py + h, px, py, r);
                    ctx.arcTo(px, py, px + w, py, r);
                    ctx.closePath();
                    ctx.fill();
                    ctx.stroke();
                }
                ctx.restore();
            },
        };

        // --- UI Elements within the widget ---
        const enabledToggle = this.node.addWidget("toggle", `Enabled`, true, () => this.node.serializeMakeupData());
        const typeSelect = this.node.addWidget("combo", `Type`, "none", () => this.node.serializeMakeupData(), { values: this.makeupData.types });
        const intensitySelect = this.node.addWidget("combo", `Intensity`, "medium", () => this.node.serializeMakeupData(), { values: this.makeupData.intensities });
        const colorSelect = this.node.addWidget("combo", `Color`, "none", () => this.node.serializeMakeupData(), { values: this.makeupData.colors });
        const duplicateButton = this.node.addWidget("button", "⎘", null, () => this.onDuplicate(this.id));
        const removeButton = this.node.addWidget("button", "🗑️", null, () => this.onRemove(this.id));

        widget.widgets = [enabledToggle, typeSelect, intensitySelect, colorSelect, duplicateButton, removeButton];
        return widget;
    }

    getValues() {
        return {
            enabled: !!this.widget.widgets[0].value,
            type: this.widget.widgets[1].value,
            intensity: this.widget.widgets[2].value,
            color: this.widget.widgets[3].value,
        };
    }

    remove() {
        this.widget.widgets.forEach(w => this.node.widgets.splice(this.node.widgets.indexOf(w), 1));
    }
}

app.registerExtension({
    name: "comfyui.outfit.makeup.v2",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "FemaleOutfitNode" || nodeData.name === "MaleOutfitNode") {
            
            const setupMakeupSystem = (node) => {
                node.makeupItems = [];
                node.makeupCounter = 0;

                const makeupDataWidget = node.addWidget("string", "makeup_data", "", { multiline: false });
                makeupDataWidget.type = "hidden";

                node.addWidget("button", "💄 Add Makeup", null, async () => {
                    const gender = nodeData.name === "FemaleOutfitNode" ? "female" : "male";
                    const makeupData = await MakeupAPI.getMakeupData(gender);
                    
                    const newItem = new MakeupItem(node, node.makeupCounter++, makeupData, (id) => {
                        const itemToRemove = node.makeupItems.find(item => item.id === id);
                        if (itemToRemove) {
                            itemToRemove.remove();
                            node.makeupItems = node.makeupItems.filter(item => item.id !== id);
                            node.serializeMakeupData();
                            node.setDirtyCanvas(true);
                        }
                    }, (id) => {
                        const orig = node.makeupItems.find(item => item.id === id);
                        if (!orig) return;
                        const clone = new MakeupItem(node, node.makeupCounter++, makeupData, (rid) => {
                            const itemToRemove = node.makeupItems.find(it => it.id === rid);
                            if (itemToRemove) {
                                itemToRemove.remove();
                                node.makeupItems = node.makeupItems.filter(it => it.id !== rid);
                                node.serializeMakeupData();
                                node.setDirtyCanvas(true);
                            }
                        }, node.onDuplicate);
                        // Attempt to copy selections
                        const vals = orig.getValues();
                        const widgets = clone.widget.widgets;
                        widgets[0].value = vals.enabled;
                        widgets[1].value = vals.type;
                        widgets[2].value = vals.intensity;
                        widgets[3].value = vals.color;
                        node.makeupItems.push(clone);
                        node.serializeMakeupData();
                        node.setDirtyCanvas(true);
                    });
                    
                    node.makeupItems.push(newItem);
                    node.serializeMakeupData();
                    node.setDirtyCanvas(true);
                });

                node.addWidget("button", "🧹 Clear All Makeup", null, () => {
                    node.makeupItems.forEach(it => it.remove());
                    node.makeupItems = [];
                    node.serializeMakeupData();
                    node.setDirtyCanvas(true);
                });

                node.serializeMakeupData = () => {
                    const data = node.makeupItems
                        .map(item => item.getValues())
                        .filter(val => val.enabled && val.type !== "none");
                    makeupDataWidget.value = JSON.stringify(data);
                };
            };

            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                onNodeCreated?.apply(this, arguments);
                setupMakeupSystem(this);
            };
        }
    },
});