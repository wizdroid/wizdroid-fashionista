# Wizdroid ComfyUI Outfit Selection

<p align="center">
  <img src="icon.svg" alt="Wizdroid Outfits" width="64" height="6### Mak- **Sprite Sheets**: Game-ready character sprites

## 📋 Prerequisiteslick the Makeup field to open the animated editor
- Add items like lipstick, eyeliner, blush, highlighter
- Use Enable/Duplicate/Clear All controls for quick edits

### Avoid Terms
- Use the Avoid field to list items you don't want (comma-separated or free text)
- These are appended as "Avoid: ..." in the final prompt

### Export Preset
- Toggle "export_preset" to print a preset JSON snippet to the console
- Paste under your gender in `data/presets.json` and give it a name
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
- **Female & Male Outfit Nodes**: Generate complete outfits with intelligent randomization
- **Extensive Customization**: 20+ outfit categories (torso, legs, feet, accessories, etc.)
- **Smart Presets**: Curated presets per gender that auto-fill only empty fields
- **JSON-Based Data**: Easily customizable outfit options via JSON files
- **Seed Management**: Fixed, random, increment, and decrement modes

### 🤖 AI-Powered Enhancement
- **Ollama LLM Integration**: Enhance prompts with local AI models (✨ Ollama Prompter)
- **Simple Ollama**: Streamlined prompt enhancement (🎯 Simple Ollama)
- **Vision Node Support**: Describe images using vision-language models (👁️ Ollama Vision)
- **Style Helper**: Professional photo styling assistance (📸 Photo Style Helper)
- **Character Sheets**: Generate detailed character turnarounds and expression sheets (👤 Character Sheet Generator)

### 🎨 Advanced Customization
- **Makeup UI**: Animated, toggleable makeup editor with duplicate/clear controls
- **Style Controls**: Art styles, lighting, cameras, and scene composition
- **Background Options**: Diverse scene and environment settings
- **Age & Demographics**: Comprehensive character customization
- **Avoid Terms**: Add negative keywords (e.g., blurry, low-res) to refine outputs
- **Preset Export**: Export current settings as JSON snippets for reuse
- **Preset Patch Applier**: Apply and merge preset configurations (🧩 Preset Patch Applier)

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
2. Look for nodes in these categories:
   - **Wizdroid/Outfits**: Core outfit generation and expression nodes
     - **Dynamic**: ♀️ Female Outfit, ♂️ Male Outfit
     - **Presets**: ♀️ Female Preset Outfit, ♂️ Male Preset Outfit  
     - **Expression**: 🎭 Facial Expression & Lighting
   - **Wizdroid/AI**: AI-powered enhancement nodes
     - **LLM**: ✨ Ollama Prompter, 🎯 Simple Ollama, 🚀 Lightweight Prompter
     - **Vision**: 👁️ Ollama Vision, 👁️ Lightweight Vision
   - **Wizdroid/Utils**: Utility and helper nodes
     - **Style**: 📸 Photo Style Helper, 🎨 Image Validator
     - **Character**: 👤 Character Sheet Generator
     - **Data**: 🧩 Preset Patch Applier, 🧾 Outfit Inputs From JSON

#### Core Outfit Nodes
- **👗 Female Outfit Node**: Generate female outfits with full customization
- **👔 Male Outfit Node**: Generate male outfits with full customization

#### AI Enhancement Nodes
- **✨ Ollama Prompter**: Advanced prompt enhancement with local AI models
- **🎯 Simple Ollama**: Streamlined prompt enhancement
- **👁️ Ollama Vision**: Describe images using vision-language models
- **📸 Photo Style Helper**: Professional photo styling assistance

#### Utility Nodes
- **👤 Character Sheet Generator**: Create character turnarounds, expression sheets, and action poses
- **🧩 Preset Patch Applier**: Apply and merge preset configurations
- **🔄 Outfit Inputs from JSON**: Bridge nodes for JSON-based outfit input

### Example Workflows

#### Basic Outfit Generation
```
[Female/Male Outfit Node] → [Ollama Prompter] → [Your Image Generation Model]
```

#### Character Sheet Creation
```
[Character Sheet Generator] → [Text Output] → [Image Generation Model]
```

#### Advanced Workflow with Styling
```
[Female Outfit Node] → [Photo Style Helper] → [Ollama Prompter] → [Image Generation]
```

### Using Presets
- Choose a Preset from the dropdown to auto-fill empty fields
- Presets include pose, background, scene highlights (mood, time, color scheme), and optional makeup
- You can override any field after applying a preset
- Use "Export Preset" to save your current configuration as JSON

**Notes:**
- If a preset references an unknown key, the node logs a warning to help curate data
- Presets are loaded from `data/presets.json` under keys by gender

### Character Sheet Generation
The **Character Sheet Generator** creates detailed prompts for:
- **Character Turnarounds**: Multiple angle views (front, side, back)
- **Expression Sheets**: Emotional expressions and facial studies
- **Action Pose Sheets**: Dynamic poses and movement studies
- **Outfit Sheets**: Clothing and accessory variations
- **Anatomy Studies**: Detailed anatomical references
- **Sprite Sheets**: Game-ready character sprites

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

### Optional Dependencies (for AI Features)
For AI prompt enhancement and vision capabilities:

```bash
pip install -r requirements.txt
```

**Ollama Integration:**
- Install [Ollama](https://ollama.ai/) for local AI model support
- Download models for different capabilities:
  - Text enhancement: `ollama pull llama2`, `ollama pull mistral`
  - Vision support: `ollama pull llava`, `ollama pull moondream`
  - Code generation: `ollama pull codellama`

**Vision Node Requirements:**
- Additional Python packages may be required for vision features
- Models like `llava` and `moondream` provide image description capabilities

## 🧩 Data & Extensibility

### Customizing Outfit Options
- Edit JSON files in `data/outfit/<gender>/*.json`
- Each file contains an `attire` array with outfit objects
- The node automatically discovers parts and prepends control values: `none`, `random`

### Adding New Presets
Edit `data/presets.json`:
- Top-level keys: `female`, `male`
- Under each gender, add presets by name mapping to `{ part_or_option_key: value }`
- Only valid input keys will be applied; invalid keys log warnings
- Keep values aligned with available options in the corresponding JSONs

### Extending Styles and Scenes
Modify files under `data/styles/`:
- **Scene Controls**: `mood`, `time_of_day`, `weather`, `color_scheme`
- **Style Controls**: `description_style`, `creative_scale`
- **Enhancement Data**: Photo styling and prompt enhancement templates
- All style definitions are easily customizable and extensible

### Character Sheet Templates
The Character Sheet Generator supports multiple template types:
- **Turnaround Sheets**: Multi-angle character views
- **Expression Studies**: Facial expression variations
- **Action Poses**: Dynamic movement and action shots
- **Outfit Variations**: Clothing and accessory studies
- **Anatomy References**: Detailed character studies

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📁 Project Structure

```
wizdroid-fashionista/
├── nodes/                          # Core ComfyUI node implementations
│   ├── dynamic_outfit.py          # Main outfit generation nodes
│   ├── preset_node.py             # Preset management
│   └── preset_outfit_node.py      # Preset-based outfit nodes
├── support_nodes/                  # AI and utility support nodes
│   ├── character_sheet_generator.py # Character sheet creation
│   ├── ollama_llm.py              # Enhanced LLM integration
│   ├── ollama_vision.py           # Vision model support
│   ├── simple_ollama.py           # Simplified LLM interface
│   ├── style_helper.py            # Photo styling assistance
│   ├── preset_patch_applier.py    # Preset management
│   └── outfit_inputs_from_json.py # JSON bridge nodes
├── utils/                          # Shared utilities and libraries
│   ├── data_loader.py             # Data loading and caching
│   ├── prompt_builder.py          # Prompt construction
│   ├── common.py                  # Common utilities
│   └── ollama_base.py             # Base Ollama functionality
├── data/                           # JSON configuration files
│   ├── outfit/                    # Outfit definitions by gender
│   │   ├── female/                # Female outfit categories
│   │   └── male/                  # Male outfit categories
│   ├── styles/                    # Styling and enhancement data
│   ├── presets.json              # Curated outfit presets
│   ├── backgrounds.json          # Background options
│   ├── race.json                 # Character demographics
│   └── age_groups.json           # Age group definitions
├── web/                           # Custom UI components
│   ├── beautiful_ui.js           # Enhanced UI functionality
│   └── makeup_ui.js              # Makeup editor interface
├── tests/                         # Comprehensive test suite
└── example_workflows/             # Example ComfyUI workflows
```
