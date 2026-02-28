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
  - `tui/` - Textual-based Terminal User Interface
    - `app.py` - Main TUI application
    - `widgets/` - Reusable UI components (graphs, tables, dialogs)
    - `layouts/` - Grid-based responsive layouts
    - `config.py` - Theme and layout configuration
- `cli.py` - Click-based CLI wrapper
- `tests/` - Pytest test suite with fixtures
  - `tui/` - TUI-specific tests using Textual's testing framework
- `docs/plans/` - Design documents

## Architecture

### Data Flow
1. **Data Loading** (`data.py`) - CSV parsing, column auto-detection, null handling
2. **Mode Detection** (`data.py`) - Auto-detects classification vs regression based on data types
3. **Evaluation** (`evaluator.py`) - Core orchestration, delegates to mode-specific metrics
4. **Metrics Calculation** (`metrics/`) - Separate modules for classification/regression
5. **Output** - Three output paths:
   - Rich console formatting (`formatters/rich_console.py`)
   - File export (`formatters/exporters.py`) - JSON/CSV/Markdown
   - TUI (`tui/app.py`) - Interactive Textual-based interface

### TUI Architecture
- **App** (`tui/app.py`) - Main Textual application with modal screens
- **Layouts** (`tui/layouts/dashboard.py`) - Grid-based responsive layouts
- **Widgets** (`tui/widgets/`) - Reusable UI components (graphs, tables, dialogs)
- **Config** (`tui/config.py`) - Theme and layout configuration

Key pattern: TUI widgets receive `EvaluationResults` and render themselves independently.

### Key Design Patterns
- **Factory Pattern**: `Evaluator.from_csv()` for creating evaluators from files
- **Strategy Pattern**: Mode-specific metric calculation (classification vs regression)
- **Auto-detection**: Column names and evaluation mode detected automatically when not specified
- **Separation of Concerns**: Library (`evalkit/`) is independent of CLI (`cli.py`)
- **Type Safety**: Extensive use of type hints and custom enums (`types.py`)

## Testing

- Use pytest for all tests
- Test fixtures in `tests/fixtures/` (CSV files for both modes)
- Aim for high coverage on core library code
- **TUI tests**: Use `pytest-asyncio` for Textual async components
- **Fixture pattern**: Tests use `classification_results` and `regression_results` fixtures

### Testing TUI Components
```bash
# Test specific widget
uv run pytest tests/tui/test_widgets.py::test_header -v

# Run TUI integration tests (uses Textual's testing framework)
uv run pytest tests/tui/test_integration.py -v
```

### TUI Widget Development
- All widgets extend `textual.widgets.Static` or other Textual primitives
- Widgets receive `EvaluationResults` in constructor
- Use Plotext for in-terminal graphs (confusion matrix, scatter plots, bar charts)
- Modals (dialogs, help) use `push_screen()` pattern

## Code Style

- Use ruff for linting and formatting
- Line length: 100 characters
- Target Python 3.10+