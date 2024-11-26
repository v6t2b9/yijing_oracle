# yijing_oracle

A Python package for I Ching (Yijing) divination and oracle consultation. Provides tools for casting hexagrams, interpreting changes, and receiving AI-powered guidance based on traditional I Ching wisdom.

## Features

- 🎲 Automated hexagram casting using traditional methods
- 🔄 Tracking of changing lines and transformations
- 🤖 AI-powered interpretations using Google's Generative AI
- 📊 Clean, type-hinted API with Pydantic models
- 🧪 Comprehensive test coverage
- 📝 Detailed logging and debugging options

## Quick Start

```python
from yijing_oracle import ask_oracle

# Simple usage
response = ask_oracle("What should I focus on today?")
print(response['answer'])

# Advanced usage
from yijing_oracle import YijingOracle, OracleSettings

oracle = YijingOracle(
    custom_settings={
        "temperature": 0.8,
        "max_tokens": 2048
    }
)
response = oracle.get_response("Should I take this opportunity?")
```

## Configuration

The oracle can be configured using either:
- Environment variables
- A JSON configuration file
- Direct parameter passing

Required environment variable:
- `GENAI_API_KEY`: Your Google Generative AI API key

## Requirements

- Python 3.8+
- google-generativeai
- pydantic

## License

This project is licensed under Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)

### You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

### Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made
- NonCommercial — You may not use the material for commercial purposes
- No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits

[View the full license](https://creativecommons.org/licenses/by-nc/4.0/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

If you encounter any problems or have questions, please:
1. Check the [documentation](docs/)
2. Look through existing [issues](issues/)
3. Open a new issue if needed

## Acknowledgments

This project takes inspiration from traditional I Ching divination methods and combines them with modern AI technology. Special thanks to the open source community and contributors.

---

Created with ❤️ for the I Ching community