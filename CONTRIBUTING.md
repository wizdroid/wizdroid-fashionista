# Contributing to ComfyUI Outfit Selection Node

Thank you for your interest in contributing to this project! This document provides guidelines for contributing to the ComfyUI Outfit Selection Node.

## How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use clear, descriptive titles** for bug reports
3. **Include steps to reproduce** the issue
4. **Provide ComfyUI version** and system information
5. **Include error messages** and logs if applicable

### Suggesting Features

1. **Check existing feature requests** to avoid duplicates
2. **Clearly describe the feature** and its benefits
3. **Explain the use case** for the feature
4. **Consider backward compatibility** implications

### Code Contributions

#### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/wizdroid/wizdroid-fashionista.git
   cd wizdroid-fashionista
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Guidelines

1. **Follow Python conventions**:
   - Use PEP 8 style guide
   - Use meaningful variable and function names
   - Add docstrings for functions and classes

2. **Test your changes**:
   ```bash
   python -m unittest test_dynamic_outfit_updated.py -v
   python test_functional.py
   ```

3. **Update documentation** if needed:
   - Update README.md for new features
   - Update CHANGELOG.md with your changes
   - Add comments for complex logic

#### Adding New Data

##### Adding New Genders

1. Create a new folder under `data/outfit/` (e.g., `data/outfit/non-binary/`)
2. Add JSON files for each body part following the existing structure
3. Test the new node generation

##### Adding New Body Parts

1. Create a new JSON file in the appropriate gender folder
2. Follow the established JSON structure:
   ```json
   {
     "body_part": "new_part",
     "attire": [
       {"type": "item_type", "country": "neutral", "color": "color_name"}
     ]
   }
   ```
3. Test the dropdown generation

##### Adding New Options

1. Edit existing JSON files to add new items
2. Maintain consistency in data structure
3. Consider cultural sensitivity and inclusivity

#### Testing Requirements

1. **Run existing tests** to ensure nothing is broken
2. **Add new tests** for new features:
   - Unit tests for individual functions
   - Integration tests for node functionality
   - Edge case testing

3. **Test with ComfyUI** in a real environment

#### Code Style

1. **Use consistent indentation** (4 spaces)
2. **Add comments** for complex logic
3. **Use type hints** where appropriate
4. **Keep functions focused** and single-purpose

### Pull Request Process

1. **Update documentation** as needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** with your changes
5. **Submit the pull request** with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots if UI changes are involved

### Code Review Process

1. **Be responsive** to feedback
2. **Make requested changes** promptly
3. **Test thoroughly** after changes
4. **Be respectful** in discussions

## Data Guidelines

### Cultural Sensitivity

1. **Avoid stereotypes** in clothing descriptions
2. **Include diverse options** from various cultures
3. **Use respectful terminology** for cultural items
4. **Consider global perspectives** in design choices

### Bias Prevention

1. **Exclude country information** from outputs
2. **Separate race handling** from other attributes
3. **Use inclusive language** in descriptions
4. **Test for unintended bias** in outputs

### JSON Structure Standards

1. **Follow established schemas** for consistency
2. **Use clear, descriptive names** for items
3. **Include necessary attributes** (type, color, etc.)
4. **Maintain alphabetical ordering** where possible

## Community Guidelines

1. **Be respectful** to all contributors
2. **Help newcomers** get started
3. **Share knowledge** and best practices
4. **Follow the code of conduct**

## Getting Help

- **Open an issue** for questions about contributing
- **Join discussions** on existing issues
- **Review the README** for technical details
- **Check the tests** for usage examples

Thank you for contributing to making this project better for everyone!
