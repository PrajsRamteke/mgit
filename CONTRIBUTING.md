# Contributing to Multi-Git Manager

Thank you for your interest in contributing! 🎉

## Development Setup

```bash
# 1. Fork & clone
git clone https://github.com/<you>/multi-git-manager.git
cd multi-git-manager

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. Run tests
python -m pytest tests/ -v
```

## Guidelines

- **Code style**: Follow PEP 8. Use type hints.
- **Tests**: Add tests for new features. Maintain ≥ 80% coverage.
- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/).
- **Docs**: Update README and docstrings for user-facing changes.

## Reporting Issues

Open an issue with:

- OS and Python version
- Steps to reproduce
- Expected vs. actual behavior

## Feature Requests

Open an issue tagged `enhancement` describing the use case and proposed solution.

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

---

Thank you for contributing!
