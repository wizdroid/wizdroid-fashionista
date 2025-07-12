# ComfyUI Outfit Selection

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Compatible-brightgreen.svg)](https://github.com/comfyanonymous/ComfyUI)
[![GitHub release](https://img.shields.io/github/release/manifestations/comfyui-outfit.svg)](https://github.com/manifestations/comfyui-outfit/releases)

A comprehensive outfit generation system for ComfyUI with AI-powered prompt enhancement and dynamic outfit composition.

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

## 📦 Installation

### Method 1: Git Clone (Recommended)
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/manifestations/comfyui-outfit.git
```

### Method 2: Manual Download
1. Download the latest release from the [Releases](https://github.com/manifestations/comfyui-outfit/releases) page
2. Extract to `ComfyUI/custom_nodes/comfyui-outfit/`

### Method 3: ComfyUI Manager
1. Open ComfyUI Manager
2. Search for "ComfyUI Outfit Selection"
3. Click Install

## 🚀 Quick Start

### Basic Usage
1. Start ComfyUI
2. Look for nodes under **👗 Outfit** category:
   - **Female Outfit Node**: Generate female outfits
   - **Male Outfit Node**: Generate male outfits
   - **Ollama Prompter**: Enhance prompts with AI
   - **Simple Ollama**: Basic prompt enhancement

### Example Workflow
```
[Female Outfit Node] → [Text Output] → [Your Image Generation Model]
```

## 📋 Requirements

### Core Requirements
- ComfyUI (latest version)
- Python 3.8+

### Optional Dependencies
For AI prompt enhancement features:
```bash
pip install requests pillow numpy torch
```

For vision node support:
```bash
# Install Ollama locally
# Download vision models (llava, moondream, etc.)
```

## License

MIT License. See [LICENSE](LICENSE).
