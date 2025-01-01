# YiJing Oracle

A Python-based I Ching (Yijing) divination system that combines traditional wisdom with modern artificial intelligence. This package integrates the ancient practice of I Ching consultation with contemporary AI technology to provide meaningful guidance and insights.

## Overview

The YiJing Oracle project implements a sophisticated approach to I Ching consultation by bridging classical hexagram interpretation with AI-powered analysis. The system is designed to provide authentic, meaningful consultations while maintaining the depth and nuance of traditional I Ching wisdom.

### Core Features

#### Advanced Hexagram System
The package introduces a unique Hypergram concept that extends beyond traditional hexagram representation:
- Sophisticated line-state tracking using the HypergramLine system
- Complete transformation mapping between initial and resultant hexagrams
- Detailed analysis of changing lines and their implications
- Rich Unicode representation of hexagrams and lines

#### AI Integration
Flexible AI model support with multiple backend options:
- Ollama integration for local model execution
- Google's Generative AI (Gemini) support for cloud-based processing
- Customizable consultation modes (single response or dialogue)
- Context-aware prompting system for meaningful interpretations

#### Robust Architecture
Built with modern Python best practices:
- Type-safe implementation using Pydantic models for data validation
- Comprehensive error handling with custom exception hierarchy
- Detailed logging system for debugging and monitoring
- Asynchronous support for efficient processing
- Resource management system for hexagram data and prompts

#### Consultation Features
- Rich text formatting with Markdown output
- Detailed analysis of hexagram transformations
- Multi-language support (English, German, Chinese characters)
- Customizable consultation styles and prompts
- Comprehensive interpretation including imagery and judgment

## Prerequisites

Before installing YiJing Oracle, ensure you have:

1. Python 3.8 or higher
2. Ollama installed locally (for local model execution)
3. A Google Cloud account and API key (if using Gemini AI)

## Installation

Currently, YiJing Oracle is not available on PyPI. To use it, clone the repository:

```bash
git clone https://github.com/yourusername/yijing-oracle.git
cd yijing-oracle
pip install -e .
```

### Dependencies

The project requires the following Python packages:

```txt
google-generativeai>=0.3.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
aiofiles>=23.0
ollama-python>=0.1.0
pytest>=7.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
```

## Technical Architecture

### The Hypergram System

The Hypergram system represents an innovative approach to I Ching line representation:

```python
from yijing.models import HypergramLine, Hypergram

# Each line can be in one of four states:
# 6: Changing Yin  (transforming to Yang)
# 7: Stable Yang   (no transformation)
# 8: Stable Yin    (no transformation)
# 9: Changing Yang (transforming to Yin)

line = HypergramLine(value=6)  # A changing Yin line
print(line.is_changing())      # True
print(line.transforms_to())    # 1 (Yang)
```

### Pydantic Models

The system uses Pydantic for robust data validation and serialization:

```python
from yijing.models import HexagramContext

# Example of type-safe hexagram context
context = HexagramContext(
    original_hexagram=hexagram_data,
    changing_lines=[2, 3],
    resulting_hexagram=result_data
)
```

## Usage Examples

### Basic Consultation

```python
from yijing import YijingOracle
from yijing.enums import ModelType, ConsultationMode

# Initialize with Ollama
oracle = YijingOracle(
    custom_settings={
        "model_type": ModelType.OLLAMA,
        "active_model": "llama2:latest",
        "consultation_mode": ConsultationMode.SINGLE
    }
)

# Get a reading
response = oracle.get_response("What guidance can the I Ching offer?")
```

### Advanced Analysis

```python
from yijing import cast_hypergram, analysiere_hexagramm_eigenschaften

# Generate and analyze a reading
hypergram_data = cast_hypergram()
analysis = analysiere_hexagramm_eigenschaften(hypergram_data)

# Access detailed transformation information
print(f"Changing lines: {analysis['wandlungslinien_positionen']}")
print(f"Core aspects: {analysis['kernaspekte']}")
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```ini
# Required for GenAI model
GENAI_API_KEY=your-api-key

# Optional settings
DEBUG=True
LOG_LEVEL=INFO
```

### Programmatic Configuration

```python
custom_settings = {
    "model_type": ModelType.OLLAMA,
    "active_model": "llama2:latest",
    "consultation_mode": ConsultationMode.DIALOGUE,
    "debug": True
}

oracle = YijingOracle(custom_settings=custom_settings)
```

## Development

### Setting Up Development Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run tests with coverage
pytest tests/ --cov=yijing --cov-report=term-missing

# Run async tests
pytest tests/ -v --asyncio-mode=auto
```

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0).

### Terms of Use

- Share and adapt the material freely
- Provide attribution
- Non-commercial use only

For the complete license text, see [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Code style and standards
- Test requirements
- Pull request process
- Documentation guidelines

## Support

For support:

1. Check the documentation in `docs/`
2. Review existing issues
3. Open a new issue with detailed information

---

Created for the I Ching community with respect for tradition and innovation.