# Contributing to Bee Cell Annotation Tool

Thank you for your interest in contributing to the Bee Cell Annotation Tool! This document provides guidelines and information for contributors.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Screenshots** if applicable
- **Environment details** (OS, browser, Python version)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear title and description**
- **Use case** and motivation
- **Proposed solution** or implementation ideas
- **Alternative solutions** considered

### Pull Requests

1. **Fork** the repository
2. **Create a feature branch** from `main`
3. **Make your changes** following our coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.7+
- Git
- Modern web browser

### Local Development

1. Clone your fork:
```bash
git clone https://github.com/your-username/bee-cell-annotation.git
cd bee-cell-annotation
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Set up configuration:
```bash
cp .env.example .env
```

5. Run tests:
```bash
python -m pytest tests/
```

6. Start development server:
```bash
python start_app.py
```

## Coding Standards

### Python Code

- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Write **docstrings** for functions and classes
- Maximum line length: **88 characters**
- Use **meaningful variable names**

### Frontend Code

- Use **semantic HTML**
- Follow **Bootstrap conventions**
- Write **accessible** interfaces
- Test on **multiple browsers**

### Testing

- Write **unit tests** for new functions
- Include **integration tests** for features
- Maintain **test coverage** above 80%
- Use **descriptive test names**

### Documentation

- Update **README.md** for new features
- Add **docstrings** to Python code
- Include **code comments** for complex logic
- Update **API documentation** for endpoint changes

## Project Structure

```
src/
├── app/                 # Flask application
│   ├── __init__.py     # App factory
│   ├── routes.py       # URL routes
│   ├── models.py       # Data models
│   └── i18n.py         # Internationalization
├── templates/          # Jinja2 templates
├── static/            # Static assets
└── locales/           # Translation files

tests/                 # Test files
config/               # Configuration
scripts/              # Utility scripts
docs/                 # Documentation
```

## Internationalization

### Adding New Languages

1. Create translation file:
```bash
mkdir -p src/locales/{lang_code}
cp src/locales/en/messages.json src/locales/{lang_code}/messages.json
```

2. Translate all strings in the new file

3. Add language to configuration:
```python
SUPPORTED_LANGUAGES = ['en', 'zh', 'your_lang_code']
```

4. Test the new language interface

### Translation Guidelines

- Keep **consistent terminology**
- Consider **cultural context**
- Test **UI layout** with translated text
- Use **placeholders** for dynamic content

## Release Process

1. **Update version** in `setup.py`
2. **Update CHANGELOG.md**
3. **Create release branch**
4. **Run full test suite**
5. **Create pull request** to main
6. **Tag release** after merge
7. **Update documentation**

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: For security issues or private matters

## Recognition

Contributors will be recognized in:

- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page

Thank you for contributing to make this tool better for the research community!
