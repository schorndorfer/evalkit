# EvalKit: Evaluation CLI Design

**Date:** 2026-02-26
**Status:** Approved

## Overview

EvalKit is a comprehensive evaluation library and CLI tool for calculating accuracy metrics on machine learning predictions. It supports both classification and regression tasks, provides rich terminal output, file export capabilities, and visualization generation.

## Requirements

- Accept CSV files containing predicted and gold (actual) values
- Support both classification and regression evaluation modes
- Flexible CSV handling (simple 2-column or complex multi-column with column specification)
- Comprehensive suite of accuracy metrics
- Rich, formatted terminal output with colors and tables
- Export results to JSON, CSV, and Markdown formats
- Generate visualizations (confusion matrices, scatter plots, etc.)
- Auto-detect evaluation mode with option to override
- Usable as both a Python library and CLI tool

## Architecture

### Approach: Library + CLI Wrapper

Build a reusable evaluation library (`evalkit/`) that can be used programmatically, with a thin CLI wrapper providing command-line access. This provides maximum reusability and testability.

### Project Structure

```
test-project/
├── evalkit/                    # The reusable library
│   ├── __init__.py            # Public API exports
│   ├── evaluator.py           # Core evaluation logic
│   ├── metrics/               # Metric calculations
│   │   ├── __init__.py
│   │   ├── classification.py  # Classification metrics
│   │   └── regression.py      # Regression metrics
│   ├── data.py                # Data loading and validation
│   ├── formatters/            # Output formatting
│   │   ├── __init__.py
│   │   ├── rich_console.py    # Rich terminal output
│   │   ├── exporters.py       # JSON/CSV/markdown export
│   │   └── visualizers.py     # Chart generation
│   └── types.py               # Type definitions and enums
├── cli.py                     # CLI wrapper (uses Click)
├── tests/                     # Pytest tests
│   ├── fixtures/              # Sample CSV files
│   ├── test_evaluator.py
│   ├── test_metrics.py
│   ├── test_data.py
│   └── test_formatters.py
└── pyproject.toml            # Dependencies and CLI entry point
```

### Library API

```python
from evalkit import Evaluator

# Programmatic usage
evaluator = Evaluator.from_csv("predictions.csv",
                               pred_col="predicted",
                               gold_col="actual")
results = evaluator.evaluate()  # Auto-detects mode
print(results.summary())

# Or explicit mode
results = evaluator.evaluate(mode="classification")
results.to_json("metrics.json")
results.visualize()
```

### CLI Interface

```bash
evalkit evaluate <csv_file> [OPTIONS]

Options:
  --pred, -p TEXT          Column name for predictions (default: auto-detect)
  --gold, -g TEXT          Column name for gold/actual values (default: auto-detect)
  --mode, -m [classification|regression]
                           Evaluation mode (default: auto-detect)
  --output, -o PATH        Save results to file (JSON/CSV/MD based on extension)
  --visualize, -v          Generate and save visualization plots
  --viz-dir PATH           Directory for visualization outputs (default: ./eval_plots)
  --no-display             Skip terminal output (useful with --output)
  --help                   Show this message and exit
```

## Data Loading & Mode Detection

### CSV Handling (`data.py`)

- Support both simple CSVs (2 columns) and complex CSVs with column specification
- Use pandas for robust CSV parsing
- Default behavior: if CSV has exactly 2 columns, assume first is predicted, second is gold
- Allow explicit column specification via `pred_col` and `gold_col` parameters

### Auto-Detection Logic

Hybrid mode detection:
1. If user specifies `--mode`, use that explicitly
2. Otherwise, auto-detect based on data:
   - Try parsing values as floats
   - If all values are numeric with continuous distribution → regression
   - If values are strings or discrete categories → classification
   - If ambiguous (integer labels) → default to classification with warning

### Validation

- Check for missing values and report them
- Ensure predicted and gold columns have same length
- Verify column names exist in CSV
- Provide helpful error messages

Example validation output:
```
✓ Loaded 1000 samples from predictions.csv
✓ Using columns: 'predicted' and 'actual'
⚠ Found 5 rows with missing values (will be excluded)
ℹ Auto-detected mode: classification (3 unique classes)
```

## Metrics

### Classification Metrics (`metrics/classification.py`)

Using scikit-learn:
- **Accuracy** - Overall correctness
- **Precision, Recall, F1-Score** - Per-class and macro/micro/weighted averages
- **Confusion Matrix** - Visual representation
- **Support** - Samples per class
- **Cohen's Kappa** - Agreement metric
- **Matthews Correlation Coefficient (MCC)** - Balanced measure
- **Classification Report** - Comprehensive breakdown

For binary classification:
- **AUC-ROC** - Area under ROC curve (if probabilities available)
- **Specificity** - True negative rate

### Regression Metrics (`metrics/regression.py`)

Using scikit-learn and numpy:
- **MAE** - Mean Absolute Error
- **MSE** - Mean Squared Error
- **RMSE** - Root Mean Squared Error
- **R² Score** - Coefficient of determination
- **Adjusted R²** - Adjusted for predictors
- **MAPE** - Mean Absolute Percentage Error
- **Median Absolute Error** - Robust to outliers
- **Max Error** - Worst-case error
- **Explained Variance** - Proportion of variance explained

## Output Formatting

### Rich Console Output (`formatters/rich_console.py`)

Using the `rich` library:
- Header with file info, mode, sample count
- Metrics table with color coding (green for good, yellow for warnings)
- Confusion matrix as colored heatmap table (classification)
- Summary panel with key takeaways

Example output:
```
╭─────────────────────────────────────────╮
│  Evaluation Results                     │
│  Mode: Classification                   │
│  Samples: 1000                          │
╰─────────────────────────────────────────╯

┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Metric               ┃ Value   ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Accuracy             │ 0.8450  │
│ Macro Avg Precision  │ 0.8312  │
│ Macro Avg Recall     │ 0.8401  │
│ Macro Avg F1-Score   │ 0.8356  │
└──────────────────────┴─────────┘
```

### File Export (`formatters/exporters.py`)

- **JSON** - Machine-readable with all metrics
- **CSV** - Simple key-value pairs
- **Markdown** - Formatted tables for documentation

### Visualization (`formatters/visualizers.py`)

Using matplotlib and seaborn:
- **Classification**: Confusion matrix heatmap, per-class metric bar charts
- **Regression**: Scatter plot (predicted vs actual), residual plot, error distribution
- Save to PNG files

## Error Handling

User-friendly error messages:
- File not found: Clear path information
- Invalid CSV: Helpful parsing feedback
- Missing columns: Show available columns
- Empty data: Guide on fixing
- Type mismatch: Explain requirements
- Ambiguous mode: Suggest explicit flag

Graceful degradation:
- Visualization failures show warning but continue
- Skip unavailable metrics with note
- Handle edge cases (single class, constant predictions)

Validation at entry points:
- CLI validates arguments before library calls
- Library validates data before processing
- Clear exit codes (1 for user errors, 2 for internal errors)

## Testing Strategy

### Test Coverage with pytest

1. **Unit Tests:**
   - Metric calculations against known values
   - CSV parsing and validation
   - Output formatting logic

2. **Integration Tests:**
   - End-to-end evaluation workflows
   - Both classification and regression
   - Auto-detection accuracy

3. **CLI Tests:**
   - Argument parsing
   - File I/O operations
   - Error handling and exit codes

4. **Test Fixtures:**
   - Sample CSVs in `tests/fixtures/`
   - Edge cases (single sample, perfect predictions, etc.)

## Dependencies

### Core Dependencies
- `pandas>=2.0.0` - CSV handling
- `scikit-learn>=1.3.0` - Metrics
- `numpy>=1.24.0` - Numerical operations
- `click>=8.1.0` - CLI framework
- `rich>=13.0.0` - Terminal formatting
- `matplotlib>=3.7.0` - Visualization
- `seaborn>=0.12.0` - Enhanced viz

### Dev Dependencies
- `pytest>=7.4.0` - Testing
- `pytest-cov>=4.1.0` - Coverage
- `ruff>=0.1.0` - Linting/formatting

## Development Workflow

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=evalkit --cov-report=term-missing

# Lint and format
uv run ruff check .
uv run ruff format .

# Run CLI (development)
uv run python cli.py evaluate <file>

# Install as package
uv pip install -e .
```
