# Wizdroid ComfyUI Outfit Selection

<p align="center">
  <img src="icon.svg" alt="Wizdroid Outfits" width="64" height="64">
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Compatible-brightgreen.svg)](https://github.com/comfyanonymous/ComfyUI)
[![GitHub release](https://img.shields.io/github/release/wizdroid/wizdroid-fashionista.svg)](https://github.com/wizdroid/wizdroid-fashionista/releases)

A comprehensive outfit generation system for ComfyUI with AI-powered prompt enhancement and dynamic outfit composition.

## 📖 Table of Contents
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Data & Extensibility](#-data--extensibility)
- [Project Structure](#-project-structure)
- [License](#license)

## 🎯 Features

### 👗 Dynamic Outfit Generation
- **Female & Male Outfit Nodes**: Generate complete outfits with randomization
- **Extensive Customization**: 20+ outfit categories (torso, legs, feet, accessories, etc.)
- **Smart Randomization**: Intelligent random selection with seed control
- **JSON-Based Data**: Easily customizable outfit options via JSON files

### 🤖 AI-Powered Prompt Enhancement
- **Ollama LLM Integration**: Enhance prompts with local AI models
- **Vision Node Support**: Describe images using vision-language models
- **Flexible Styling**: Multiple prompt styles and creative modes
- **Professional Quality**: Production-ready prompt generation

### 🎨 Advanced Customization
- **Seed Management**: Fixed, random, increment, and decrement modes
- **Style Controls**: Art styles, lighting, cameras, and more
- **Background Options**: Diverse scene and environment settings
- **Age & Demographics**: Comprehensive character customization
 - **Smart Presets**: Curated presets per gender that auto-fill only empty fields
 - **Makeup UI**: Animated, toggleable makeup editor with duplicate/clear controls
 - **Avoid Terms**: Add negative keywords (e.g., blurry, low-res) to refine outputs
 - **Preset Export**: Toggle to print a JSON snippet of your current choices to console

## 📦 Installation

### Method 1: Git Clone (Recommended)
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/wizdroid/wizdroid-fashionista.git
```

### Method 2: Manual Download
1. Download the latest release from the [Releases](https://github.com/wizdroid/wizdroid-fashionista/releases) page
2. Extract to `ComfyUI/custom_nodes/wizdroid-fashionista/`

### Method 3: ComfyUI Manager
1. Open ComfyUI Manager
2. Search for "ComfyUI Outfit Selection"
3. Click Install

## 🚀 Quick Start

### Basic Usage
1. Start ComfyUI
2. Look for nodes under **Wizdroid/Outfits** category:
   - **Female Outfit Node**: Generate female outfits
   - **Male Outfit Node**: Generate male outfits
   - **Ollama Prompter**: Enhance prompts with AI
   - **Simple Ollama**: Basic prompt enhancement

### Example Workflow
```
[Female Outfit Node] → [Text Output] → [Your Image Generation Model]
```

### Using Presets
- Choose a Preset from the dropdown. It fills only fields that are empty/none/random.
- You can still override any field afterwards.
- Presets include pose, background, and scene highlights (mood, time, color scheme), plus optional makeup.

Notes:
- If a preset references an unknown key, the node logs a warning to help curate data.
- Presets are loaded from `data/presets.json` under keys by gender.

### Makeup Editor
### Avoid Terms
- Use the Avoid field to list items you don’t want (comma-separated or free text).
- These are appended as “Avoid: ...” in the final prompt.

### Export Preset
- Toggle “export_preset” to print a preset JSON snippet to the console.
- Paste under your gender in `data/presets.json` and give it a name.
- Click the Makeup field to open the editor.
- Add items like lipstick, eyeliner, blush, highlighter, etc.
- Use the Enable/Duplicate/Clear All controls for quick edits.

## 📋 Prerequisites

### Core Requirements
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) (latest version recommended)
- [Python](https://www.python.org/downloads/) 3.8+

### Optional Dependencies
For AI prompt enhancement features, these packages are required. They can be installed by running:
```bash
pip install -r requirements.txt
```

For vision node support:
- An Ollama installation is required.
- You will also need to download vision models (e.g., `llava`, `moondream`).

## 📦 Installation

MIT License. See [LICENSE](LICENSE).

## 🧩 Data & Extensibility

### Add or Edit Outfit Options
- Edit JSON files in `data/outfit/<gender>/*.json`. Each file contains an `attire` array of objects with a `type` string.
- The node automatically discovers parts and prepends control values: `none`, `random`.

### Add Presets
- Edit `data/presets.json`:
   - Top-level keys: `female`, `male`.
   - Under each, add presets by name mapping to `{ part_or_option_key: value }`.
   - Only keys present as inputs will be applied; others are ignored with a warning.
- Keep values aligned with available options in the corresponding JSONs (poses/backgrounds included).

### Scene/Style Controls
- Tunables include: `mood`, `time_of_day`, `weather`, `color_scheme`, `description_style`, and `creative_scale`.
- Styles are defined under `data/styles/` and are easy to extend.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📁 Project Structure
The project is organized as follows:
- **`nodes/`**: Contains the core ComfyUI node implementations.
- **`utils/`**: Shared utilities for data loading and prompt building.
- **`data/`**: JSON files for outfits, presets, and styles.
- **`web/`**: Custom UI components (CSS, JS).
- **`tests/`**: Unit tests for the project.
- **`__init__.py`**: Registers the custom nodes with ComfyUI.
- **`requirements.txt`**: Lists the Python dependencies.
