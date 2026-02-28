# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EvalKit: A comprehensive evaluation library and CLI tool for calculating accuracy metrics on ML predictions. Supports both classification and regression tasks with rich terminal output, file export, and visualizations.

Python project managed with `uv`.

## Development Commands

### Running the CLI
```bash
# Run the CLI (development mode)
uv run python cli.py evaluate <csv_file>

# Run with options
uv run python cli.py evaluate predictions.csv --pred predicted --gold actual --mode classification

# After installation
evalkit evaluate <csv_file>
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=evalkit --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_evaluator.py
```

### Linting and Formatting
```bash
# Check code with ruff
uv run ruff check .

# Format code with ruff
uv run ruff format .
```

### Package Management
```bash
# Install dependencies
uv sync

# Add a dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Install as editable package
uv pip install -e .
```

### TUI Development
```bash
# Run TUI in development
uv run python cli.py evaluate <file> --tui

# Test different layouts
uv run python cli.py evaluate <file> --tui --tui-layout minimal

# Run TUI tests
uv run pytest tests/tui/ -v
```

## Project Structure

- `evalkit/` - Core library package
  - `evaluator.py` - Main evaluation logic
  - `data.py` - CSV loading and validation
  - `types.py` - Type definitions and enums
  - `metrics/` - Classification and regression metrics
  - `formatters/` - Rich console output, exporters, visualizers
- `cli.py` - Click-based CLI wrapper
- `tests/` - Pytest test suite with fixtures
- `docs/plans/` - Design documents

## Testing

- Use pytest for all tests
- Test fixtures in `tests/fixtures/`
- Aim for high coverage on core library code

## Code Style

- Use ruff for linting and formatting
- Line length: 100 characters
- Target Python 3.10+