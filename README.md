# ComfyUI Outfit Nodes

Advanced, professional outfit and makeup generation nodes for ComfyUI, with dynamic UI and AI-powered prompt formatting.

## Features

- **Dynamic Outfit Generation**: Customizable nodes for male and female characters
- **Dynamic Makeup & Accessories**: Add/remove/enable/disable multiple makeup and accessory/tattoo items, each with color/material selection
- **Gender-Specific Poses**: Loads poses and options based on selected gender
- **AI-Powered Descriptions**: Simple Ollama Node generates vivid, natural prompts (SDXL/Flux) with detailed makeup, body shape, and clothing descriptions
- **Modern UI**: User-friendly, dynamic controls for all options

## Installation

1. Place this folder in your ComfyUI `custom_nodes` directory:
   ```
   ComfyUI/custom_nodes/comfyui-outfit/
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Restart ComfyUI

## Main Nodes

- **Female Outfit Node**: Full female character outfit, makeup, and accessories
- **Male Outfit Node**: Full male character outfit and accessories
- **Simple Ollama Node**: AI prompt generator (SDXL/Flux styles, vivid makeup/body/clothing descriptions)
- **Ollama Vision Node**: (Optional) AI image analysis for outfit suggestions

## Usage

1. Add a Female or Male Outfit Node to your workflow
2. Configure attributes (body type, pose, background, etc.)
3. Use the dynamic UI to add makeup and accessories/tattoos, selecting color/material for each
4. Connect to the Simple Ollama Node for advanced prompt formatting
5. Use "random" for any attribute to randomize

## Data Structure

- All options are in `data/outfit/female/` and `data/outfit/male/` (JSON)
- Shared options (colors, intensities, materials) in `data/makeup.json`
- Gender-specific poses in `data/outfit/female/poses.json` and `data/outfit/male/poses.json`

## Troubleshooting

- **UI not updating**: Restart ComfyUI after updates
- **Missing options**: Check JSON files in `data/`
- **AI nodes not working**: Ensure Ollama is installed and running locally

## License

MIT License. See [LICENSE](LICENSE).
