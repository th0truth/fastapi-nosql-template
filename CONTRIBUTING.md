# Contributing to FastAPI NoSQL Template

Thank you for your interest in contributing to **FastAPI NoSQL Template**. Contributions are essential for maintaining a high-performance, robust, and clean framework for the community.

This project follows an async-first philosophy emphasizing clean abstractions, strict typing, complete test coverage, and strict compliance with PEP 8 standards.

---

## Getting Started

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Package Manager)
- Docker & Docker Compose

### Local Environment Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/th0truth/fastapi-nosql-template.git
   cd fastapi-nosql-template
   ```

2. **Install Dependencies**
   ```bash
   uv sync
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   ```

4. **Start Application Stack**
   ```bash
   docker compose up --build
   ```

---

## Development Workflow

### Branching Strategy
- `master`: Main production-ready branch.
- Feature branches: `feat/feature-name`
- Bug fixes: `fix/issue-description`

### Code Quality & Standards
All contributions must adhere to the following guidelines:
- **PEP 8 Compliance**: Strict compliance with PEP 8 guidelines, 2-space indentation width, and explicit line length limits ($\le 88$ characters).
- **Type Annotations**: Full typing on all functions, classes, and methods.
- **Asynchronous I/O**: Use `async/await` syntax for all I/O operations.
- **Pydantic v2**: Use Pydantic v2 models for schema validation.
- **Linting & Formatting**: Ensure `ruff` checks and formatting pass prior to submitting code:
  ```bash
  uv run ruff check .
  uv run ruff format --config 'indent-width=2' .
  ```
- **Custom Indentation Width**: To convert the codebase to 4-space indentation for local development or project standards:
  ```bash
  uv run ruff format --config 'indent-width=4' .
  ```

### Testing & Coverage
We enforce high test coverage across all core modules:
- **Execute Test Suite**:
  ```bash
  uv run pytest
  ```
- **Verify Coverage**:
  ```bash
  uv run pytest --cov=src
  ```

---

## Submitting Contributions

### Reporting Issues
When reporting a bug, please create a clear issue detailing:
- Summary and steps to reproduce.
- Expected versus actual behavior.
- Operating system and Python environment specifications.

### Pull Requests
1. Create a focused branch for your changes.
2. Implement your changes following PEP 8 and project style guidelines.
3. Add unit or integration tests to cover new functionality.
4. Verify all linting rules and test suites pass locally.
5. Submit a pull request with a descriptive summary of your changes.

---

## License

By contributing to this repository, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
