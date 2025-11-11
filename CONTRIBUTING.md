# Contributing to Tooner

Thank you for your interest in contributing to Tooner! This Claude Code hook helps users reduce LLM token costs through automatic JSON compression.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/tooner.git
   cd tooner
   ```

3. Set up development environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

## Development Workflow

### Running Tests

```bash
pytest
```

### Code Formatting

We use `black` and `ruff` for code formatting:

```bash
black src/ tests/
ruff check src/ tests/ --fix
```

### Testing Locally

Test the hook directly:

```bash
# Test the hook with sample data
echo '{"prompt": "test [{\\"a\\":1},{\\"a\\":2},{\\"a\\":3}]"}' | python hooks/compress_prompt.py
```

Test the MCP test server (optional):

```bash
python src/tooner/server.py
```

### Docker Testing

Build and test the Docker image:

```bash
docker build -t tooner-mcp:test .
docker run -i --rm tooner-mcp:test
```

## Contribution Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all public functions
- Keep functions focused and concise

### Testing

- Write tests for all new features
- Ensure existing tests pass
- Aim for >80% code coverage

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add new compression algorithm
fix: handle edge case in toon_to_json
docs: update installation instructions
test: add tests for nested structures
```

### Pull Requests

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests and linting
4. Commit your changes
5. Push to your fork
6. Create a Pull Request with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots/examples if applicable

## Areas for Contribution

We welcome contributions in these areas:

### Features
- Support for more data formats
- Integration with tiktoken for accurate token counting
- Performance optimizations
- Additional MCP tools for data analysis

### Documentation
- Usage examples
- Tutorial videos
- Blog posts
- Integration guides

### Testing
- Edge case coverage
- Performance benchmarks
- Integration tests

### Community
- Docker Hub optimization
- CI/CD pipeline improvements
- Security enhancements

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about the codebase
- General discussion

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to build something useful for the community.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
