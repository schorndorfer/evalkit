# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python project managed with `uv`. The main entry point is `main.py`.

## Development Commands

### Running the Application
```bash
# Run the main script
uv run python main.py

# Or with standard Python
python main.py
```

### Package Management
```bash
# Add a dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Sync dependencies
uv sync
```

## Project Structure

This is currently a minimal Python project with:
- `main.py` - Entry point with a `main()` function
- `pyproject.toml` - Project metadata and dependencies
- For unit tests, let's use pytest. Use ruff for linting and formatting