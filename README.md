# yijing_oracle

A Python package for I Ching (Yijing) divination and oracle consultation using Generative AI. Provides automated hexagram casting, interpretation of changes, and AI-powered guidance based on traditional I Ching wisdom.

## Features

- Automated hexagram casting with changing lines tracking
- AI-powered interpretations using Google's Generative AI
- Support for both single-response and dialogue consultation modes
- Type-safe implementation with Pydantic models
- Detailed logging and debugging capabilities
- Configurable system prompts and consultation styles

## Installation

```bash
pip install yijing-oracle
```

## Quick Start

```python
from yijing_oracle import ask_oracle

# Simple usage with environment variable GENAI_API_KEY
response = ask_oracle("What should I focus on today?")
print(response['answer'])

# Advanced usage with explicit configuration
from yijing_oracle import YijingOracle, ConsultationMode

oracle = YijingOracle(
    api_key="your-api-key",
    custom_settings={
        "active_model": "models/gemini-1.5-flash",
        "consultation_mode": ConsultationMode.DIALOGUE
    }
)

# Start a dialogue consultation
oracle.start_new_consultation()
response = oracle.get_response("Should I take this opportunity?")
```

## Configuration

Configure the oracle via:
- Environment variables
- Direct parameter passing
- JSON configuration file

Required:
- `GENAI_API_KEY`: Your Google Generative AI API key

## Requirements

- Python 3.8+
- google-generativeai
- pydantic
- pydantic-settings

## License

CC BY-NC 4.0 (Creative Commons Attribution-NonCommercial 4.0 International)

### Terms:
- Share and adapt the material freely
- Provide attribution
- Non-commercial use only

[Full License](https://creativecommons.org/licenses/by-nc/4.0/)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## Support

1. Check documentation in `docs/`
2. Review existing issues
3. Open new issue if needed

---

Created for the I Ching community