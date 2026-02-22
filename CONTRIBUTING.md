# Contributing to FastAPI NoSQL Template

First off, thank you for considering contributing to the FastAPI NoSQL Template! It's people like you who make this project a great tool for the community.

This project follows a high-performance, async-first philosophy. We value clean abstractions, strict typing, and comprehensive testing.

## 🏁 Getting Started

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (for lightning-fast dependency management)
- Docker and Docker Compose

### Local Setup
1. Fork the repository and clone it locally.
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Set up your environment:
   ```bash
   cp .env.example .env
   ```
4. Run the development environment:
   ```bash
   docker compose up --build
   ```

## 🛠️ Development Workflow

### Branching
- `master`: The stable branch.
- Feature branches: `feat/your-feature-name`
- Bug fix branches: `fix/issue-description`

### Code Style
We strictly adhere to modern Python standards:
- **Typing**: All functions and methods must have type hints.
- **Async**: Use `async/await` for all I/O operations.
- **Pydantic**: Use Pydantic v2 models for data validation.
- **Linting/Formatting**: We use `ruff` for linting and formatting. Run it before committing:
  ```bash
  uv run ruff check .
  uv run ruff format .
  ```

### Testing
We maintain **100% test coverage**. Every new feature or bug fix must include tests.
- Run tests:
  ```bash
  uv run pytest
  ```
- Check coverage:
  ```bash
  uv run pytest --cov=src
  ```

## 🤝 How to Contribute

### Reporting Bugs
If you find a bug, please open an issue and include:
- A clear description of the bug.
- Steps to reproduce the issue.
- Expected vs. actual behavior.
- Environment details (OS, Python version).

### Suggesting Enhancements
We welcome ideas for new features! When suggesting an enhancement:
- Explain why the feature is needed.
- Provide examples of how it would be used.
- Consider if it fits the "minimalist backbone" philosophy.

### Pull Requests
1. Create a branch for your changes.
2. Write clean, documented code.
3. Add or update tests to ensure coverage remains at 100%.
4. Ensure all linting and tests pass locally.
5. Submit a PR with a clear description of your changes.

## 📜 License
By contributing, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE).

---

**Thank you for helping build the future of NoSQL-native FastAPI applications!** ⚡
