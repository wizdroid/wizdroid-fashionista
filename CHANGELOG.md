# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-09-15

### Added
- **Character Sheet Generator**: New support node (`👤 Character Sheet Generator`) for creating detailed prompts for character turnarounds, expression sheets, and action poses
- **Comprehensive README**: Updated documentation with detailed node descriptions, workflow examples, and project structure
- **Enhanced Node Organization**: Improved categorization with emoji icons for better UX

### Changed
- **Project Structure**: Moved core outfit logic from root `dynamic_outfit_node.py` to organized `nodes/dynamic_outfit.py`
- **Requirements Optimization**: Streamlined `requirements.txt` to include only essential dependencies (requests, pillow, numpy)
- **Documentation Overhaul**: Complete README.md restructure with current node listings and usage examples

### Removed
- **Redundant Files**: Removed `dynamic_outfit_node.py` from root (replaced by `nodes/dynamic_outfit.py`)
- **Backup Files**: Cleaned up `data/presets_backup.json` and `data/presets_combined_backup.json`
- **Unused Dependencies**: Moved `torch` to optional since it's assumed available in ComfyUI environment

### Fixed
- **Setup Script**: Updated `setup.py` to reference correct node file paths after restructuring


## [2.0.1] - 2025-08-28

### Fixed
- Remove noisy "No such file or directory" logs in OptimizedOllamaLLMNode for optional style files. Detail scale options are derived from `data/styles/scale_instructions.json`, and creative mode instructions are only loaded if present.

### Changed
- Treat `detail_scales.json`, `creative_modes.json`, and `creative_mode_instructions.json` as optional with sensible defaults.

## [2.0.0] - 2025-01-12

### Added
- **Project Nightingale**: Complete code hardening and optimization
- **Modular Architecture**: Comprehensive `utils/` package with shared utilities
- **Optimized Support Nodes**: Enhanced Ollama LLM and Vision nodes
- **Production-Ready Implementation**: Professional code standards and structure
- **Comprehensive Test Suite**: Unit tests with >85% coverage target
- **Enhanced Error Handling**: Graceful degradation and informative error messages
- **Seed Management**: Fixed, random, increment, and decrement modes
- **Base Classes**: Shared functionality via `BaseOllamaNode`
- **Type Safety**: Full type hints and mypy compliance
- **Code Quality Tools**: Black, isort, flake8, pylint, bandit integration

### Changed
- **Complete Refactor**: All nodes refactored for maintainability
- **Data Loading**: Optimized with caching and validation
- **Prompt Generation**: Enhanced with modular prompt building
- **Package Structure**: Professional organization and imports
- **Documentation**: Comprehensive inline documentation and docstrings

### Fixed
- **Import Issues**: Resolved all import and dependency conflicts
- **Security Vulnerabilities**: Addressed all security concerns
- **Performance Issues**: Optimized data loading and API calls
- **Memory Management**: Improved resource usage and cleanup

### Technical Details
- **Lines of Code**: 3,000+ lines refactored and optimized
- **Cyclomatic Complexity**: Reduced through modular design
- **Code Duplication**: Eliminated via shared utilities
- **Error Handling**: Robust error handling throughout
- **Testing**: Comprehensive test framework established

## [1.0.0] - 2024-12-XX

### Added
- **Core Outfit Generation**: Female and Male outfit nodes
- **Dynamic UI**: Interactive controls for outfit customization
- **AI Integration**: Ollama LLM and Vision node support
- **JSON Data Structure**: Flexible outfit and style definitions
- **Randomization**: Smart random selection with seed control
- **Style System**: Art styles, lighting, and scene controls
- **Background Options**: Diverse environment and scene settings
- **Age Demographics**: Character age and demographic options
- **Makeup System**: Dynamic makeup and accessory controls
- **Pose System**: Gender-specific poses and positioning

### Features
- 20+ outfit categories (torso, legs, feet, accessories, etc.)
- 100+ style options across multiple categories
- AI-powered prompt enhancement
- Vision-based image description
- Flexible seed management
- Professional UI integration
- Comprehensive customization options

### Initial Release
- ComfyUI custom node implementation
- JSON-based data structure
- Web UI components
- Example workflows
- Basic documentation
