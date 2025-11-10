# File: CONTRIBUTING.md
# Purpose: Contribution guidelines

# Contributing to SynergyScope

Thank you for your interest in contributing to SynergyScope!

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/synergyscope.git`
3. Create a virtual environment: `python -m venv venv`
4. Install dependencies: `pip install -r backend/requirements.txt`
5. Create a feature branch: `git checkout -b feature/your-feature-name`

## Code Standards

- Follow PEP 8 for Python code
- Use type hints for function signatures
- Write docstrings for all public functions and classes
- Add tests for new features
- Keep functions focused and under 50 lines when possible

## Testing

Run tests before submitting:
```bash
pytest tests/ --cov=backend
```

## Pull Request Process

1. Update documentation for any changed functionality
2. Ensure all tests pass
3. Update the README.md if needed
4. Submit PR with clear description of changes

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
