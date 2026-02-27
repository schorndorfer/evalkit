# Textual TUI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an interactive Terminal User Interface (TUI) to EvalKit using Textual framework with dashboard layout, in-terminal graphs, and full keyboard/mouse support.

**Architecture:** Hybrid approach - keep existing evaluation logic unchanged, create new `evalkit/tui/` module with Textual widgets. CLI integration via `--tui` flag. Reuse existing `EvaluationResults` objects, create TUI-specific formatters.

**Tech Stack:** Textual (TUI framework), plotext (terminal graphs), textual-plotext (integration), existing Rich/Click/scikit-learn stack.

---

## Phase 1: Setup & Basic Framework

### Task 1: Add Dependencies

**Files:**
- Modify: `pyproject.toml`

**Step 1: Update dependencies**

Add to dependencies section:
```toml
dependencies = [
    # ... existing dependencies ...
    "textual>=0.47.0",
    "textual-plotext>=0.2.0",
    "plotext>=5.2.0",
]
```

**Step 2: Sync dependencies**

Run: `uv sync`
Expected: Successfully installs textual, textual-plotext, plotext

**Step 3: Verify imports**

Run: `uv run python -c "import textual; import plotext; print('OK')"`
Expected: "OK"

**Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "feat: add Textual TUI dependencies"
```

---

### Task 2: Create TUI Module Structure

**Files:**
- Create: `evalkit/tui/__init__.py`
- Create: `evalkit/tui/app.py`
- Create: `evalkit/tui/widgets/__init__.py`
- Create: `evalkit/tui/layouts/__init__.py`

**Step 1: Create directories**

Run: `mkdir -p evalkit/tui/widgets evalkit/tui/layouts`

**Step 2: Create tui/__init__.py**

```python
"""Textual TUI module for EvalKit."""

from evalkit.tui.app import EvalKitApp

__all__ = ["EvalKitApp"]
```

**Step 3: Create minimal app.py**

```python
"""Main Textual application for EvalKit TUI."""

from textual.app import App
from evalkit.types import EvaluationResults


class EvalKitApp(App):
    """EvalKit TUI Application."""

    def __init__(self, results: EvaluationResults):
        """Initialize app with evaluation results."""
        super().__init__()
        self.results = results

    def compose(self):
        """Compose the UI."""
        yield from []  # Empty for now
```

**Step 4: Create empty widget __init__.py**

```python
"""Textual widgets for EvalKit TUI."""
```

**Step 5: Create empty layouts __init__.py**

```python
"""Layout configurations for EvalKit TUI."""
```

**Step 6: Test basic import**

Run: `uv run python -c "from evalkit.tui import EvalKitApp; print('OK')"`
Expected: "OK"

**Step 7: Commit**

```bash
git add evalkit/tui/
git commit -m "feat: create TUI module structure"
```

---

### Task 3: Add TUI Flag to CLI

**Files:**
- Modify: `cli.py`
- Test: Manual

**Step 1: Add --tui option to CLI**

In `cli.py`, add after `--no-display` option:

```python
@click.option(
    "--tui",
    is_flag=True,
    help="Launch interactive TUI (Terminal User Interface)",
)
def evaluate(csv_file, pred_col, gold_col, mode, output, visualize, viz_dir, no_display, tui):
```

**Step 2: Add TUI launch logic**

After evaluation, before display, add:

```python
        # Run evaluation
        results = evaluator.evaluate()

        # Launch TUI if requested
        if tui:
            from evalkit.tui import EvalKitApp
            app = EvalKitApp(results)
            app.run()
            sys.exit(0)

        # Display results in terminal (unless --no-display)
```

**Step 3: Test TUI flag**

Run: `uv run python cli.py evaluate tests/fixtures/classification_binary.csv --tui`
Expected: Empty TUI window opens, press Ctrl+C to quit

**Step 4: Commit**

```bash
git add cli.py
git commit -m "feat: add --tui flag to CLI"
```

---

### Task 4: Create Header Widget

**Files:**
- Create: `evalkit/tui/widgets/header.py`
- Create: `tests/tui/test_widgets.py`

**Step 1: Write failing test**

```python
"""Tests for TUI widgets."""

from evalkit.tui.widgets.header import Header
from evalkit.types import EvaluationResults, EvaluationMode
import numpy as np


def test_header_widget_classification():
    """Test header widget with classification results."""
    results = EvaluationResults(
        mode=EvaluationMode.CLASSIFICATION,
        metrics={"accuracy": 0.92},
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=50,
        excluded_count=0,
    )

    header = Header(results, "test.csv")
    assert header.results == results
    assert header.filename == "test.csv"
```

**Step 2: Run test to verify failure**

Run: `uv run pytest tests/tui/test_widgets.py::test_header_widget_classification -v`
Expected: FAIL - "No module named 'evalkit.tui.widgets.header'"

**Step 3: Create tests/tui directory**

Run: `mkdir -p tests/tui && touch tests/tui/__init__.py`

**Step 4: Write minimal header widget**

```python
"""Header widget for TUI."""

from textual.widgets import Static
from textual.containers import Container
from rich.text import Text

from evalkit.types import EvaluationResults, EvaluationMode


class Header(Container):
    """Header widget showing summary information."""

    def __init__(self, results: EvaluationResults, filename: str):
        """Initialize header widget."""
        super().__init__()
        self.results = results
        self.filename = filename

    def compose(self):
        """Compose header content."""
        mode = self.results.mode.value.title()
        samples = self.results.sample_count

        # Get top metric
        if self.results.mode == EvaluationMode.CLASSIFICATION:
            top_metric = f"Accuracy: {self.results.metrics.get('accuracy', 0):.4f}"
        else:
            top_metric = f"R²: {self.results.metrics.get('r2_score', 0):.4f}"

        header_text = f"📊 {mode} | 📁 {self.filename} | 📈 {samples} samples | {top_metric}"

        yield Static(header_text, id="header-content")

    DEFAULT_CSS = """
    Header {
        height: 3;
        background: $panel;
        border: solid $primary;
    }

    #header-content {
        padding: 1;
        text-align: center;
    }
    """
```

**Step 5: Run test to verify pass**

Run: `uv run pytest tests/tui/test_widgets.py::test_header_widget_classification -v`
Expected: PASS

**Step 6: Add test for regression**

Add to test file:

```python
def test_header_widget_regression():
    """Test header widget with regression results."""
    results = EvaluationResults(
        mode=EvaluationMode.REGRESSION,
        metrics={"r2_score": 0.996},
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=20,
        excluded_count=0,
    )

    header = Header(results, "regression.csv")
    assert header.results == results
```

**Step 7: Run tests**

Run: `uv run pytest tests/tui/test_widgets.py -v`
Expected: All tests PASS

**Step 8: Commit**

```bash
git add evalkit/tui/widgets/header.py tests/tui/
git commit -m "feat: add header widget with tests"
```

---

### Task 5: Create Footer Widget

**Files:**
- Create: `evalkit/tui/widgets/footer.py`
- Modify: `tests/tui/test_widgets.py`

**Step 1: Write failing test**

Add to test file:

```python
from evalkit.tui.widgets.footer import Footer


def test_footer_widget():
    """Test footer widget displays shortcuts."""
    footer = Footer()
    assert footer is not None
```

**Step 2: Run test**

Run: `uv run pytest tests/tui/test_widgets.py::test_footer_widget -v`
Expected: FAIL

**Step 3: Write footer widget**

```python
"""Footer widget for TUI."""

from textual.widgets import Footer as TextualFooter


class Footer(TextualFooter):
    """Custom footer with keyboard shortcuts."""

    DEFAULT_CSS = """
    Footer {
        background: $panel;
    }
    """
```

**Step 4: Run test**

Run: `uv run pytest tests/tui/test_widgets.py::test_footer_widget -v`
Expected: PASS

**Step 5: Commit**

```bash
git add evalkit/tui/widgets/footer.py tests/tui/test_widgets.py
git commit -m "feat: add footer widget with shortcuts"
```

---

### Task 6: Integrate Header and Footer into App

**Files:**
- Modify: `evalkit/tui/app.py`
- Modify: `evalkit/tui/widgets/__init__.py`

**Step 1: Update widgets __init__.py**

```python
"""Textual widgets for EvalKit TUI."""

from evalkit.tui.widgets.header import Header
from evalkit.tui.widgets.footer import Footer

__all__ = ["Header", "Footer"]
```

**Step 2: Update app.py**

```python
"""Main Textual application for EvalKit TUI."""

from textual.app import App, ComposeResult
from textual.widgets import Header as TextualHeader, Footer as TextualFooter

from evalkit.types import EvaluationResults
from evalkit.tui.widgets import Header, Footer


class EvalKitApp(App):
    """EvalKit TUI Application."""

    TITLE = "EvalKit - ML Evaluation Dashboard"
    CSS_PATH = None
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("h", "help", "Help"),
        ("?", "help", "Help"),
    ]

    def __init__(self, results: EvaluationResults, filename: str = "predictions.csv"):
        """Initialize app with evaluation results."""
        super().__init__()
        self.results = results
        self.filename = filename

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header(self.results, self.filename)
        # Content will go here
        yield Footer()

    def action_help(self) -> None:
        """Show help screen."""
        self.bell()  # Placeholder
```

**Step 3: Update CLI to pass filename**

In `cli.py`, update TUI launch:

```python
        if tui:
            from evalkit.tui import EvalKitApp
            import os
            filename = os.path.basename(csv_file)
            app = EvalKitApp(results, filename)
            app.run()
            sys.exit(0)
```

**Step 4: Test manually**

Run: `uv run python cli.py evaluate tests/fixtures/classification_binary.csv --tui`
Expected: TUI with header and footer visible

**Step 5: Commit**

```bash
git add evalkit/tui/app.py evalkit/tui/widgets/__init__.py cli.py
git commit -m "feat: integrate header and footer into TUI app"
```

---

## Phase 2: Metrics Display

### Task 7: Create Summary Metrics Widget

**Files:**
- Create: `evalkit/tui/widgets/summary_metrics.py`
- Modify: `tests/tui/test_widgets.py`

**Step 1: Write failing test**

```python
from evalkit.tui.widgets.summary_metrics import SummaryMetrics


def test_summary_metrics_classification():
    """Test summary metrics for classification."""
    results = EvaluationResults(
        mode=EvaluationMode.CLASSIFICATION,
        metrics={
            "accuracy": 0.92,
            "macro_avg_precision": 0.91,
            "macro_avg_recall": 0.90,
            "macro_avg_f1_score": 0.905,
            "cohen_kappa": 0.84,
        },
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=50,
    )

    widget = SummaryMetrics(results)
    assert widget.results == results
```

**Step 2: Run test**

Run: `uv run pytest tests/tui/test_widgets.py::test_summary_metrics_classification -v`
Expected: FAIL

**Step 3: Write summary metrics widget**

```python
"""Summary metrics widget for TUI."""

from textual.containers import Container, Horizontal
from textual.widgets import Static
from rich.panel import Panel
from rich.text import Text

from evalkit.types import EvaluationResults, EvaluationMode


class MetricBox(Static):
    """Single metric display box."""

    def __init__(self, label: str, value: float):
        """Initialize metric box."""
        content = f"[bold]{label}[/bold]\n[cyan]{value:.4f}[/cyan]"
        super().__init__(content)

    DEFAULT_CSS = """
    MetricBox {
        border: solid $primary;
        padding: 1;
        margin: 0 1;
        width: 20;
        height: 5;
    }
    """


class SummaryMetrics(Container):
    """Summary metrics widget showing key metrics."""

    def __init__(self, results: EvaluationResults):
        """Initialize summary metrics widget."""
        super().__init__()
        self.results = results

    def compose(self):
        """Compose summary metrics content."""
        metrics = self.results.metrics

        if self.results.mode == EvaluationMode.CLASSIFICATION:
            yield Horizontal(
                MetricBox("Accuracy", metrics.get("accuracy", 0)),
                MetricBox("Precision", metrics.get("macro_avg_precision", 0)),
                MetricBox("Recall", metrics.get("macro_avg_recall", 0)),
            )
            yield Horizontal(
                MetricBox("F1-Score", metrics.get("macro_avg_f1_score", 0)),
                MetricBox("Cohen's Kappa", metrics.get("cohen_kappa", 0)),
            )
        else:  # Regression
            yield Horizontal(
                MetricBox("R² Score", metrics.get("r2_score", 0)),
                MetricBox("MAE", metrics.get("mae", 0)),
                MetricBox("RMSE", metrics.get("rmse", 0)),
            )
            yield Horizontal(
                MetricBox("MAPE", metrics.get("mape", 0) if metrics.get("mape") is not None else 0),
            )

    DEFAULT_CSS = """
    SummaryMetrics {
        height: auto;
        padding: 1;
    }

    SummaryMetrics Horizontal {
        height: auto;
        width: 100%;
    }
    """
```

**Step 4: Run test**

Run: `uv run pytest tests/tui/test_widgets.py::test_summary_metrics_classification -v`
Expected: PASS

**Step 5: Add regression test**

```python
def test_summary_metrics_regression():
    """Test summary metrics for regression."""
    results = EvaluationResults(
        mode=EvaluationMode.REGRESSION,
        metrics={
            "r2_score": 0.996,
            "mae": 4900.0,
            "rmse": 4919.35,
            "mape": 0.0186,
        },
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=20,
    )

    widget = SummaryMetrics(results)
    assert widget.results == results
```

**Step 6: Run tests**

Run: `uv run pytest tests/tui/test_widgets.py -k summary -v`
Expected: All pass

**Step 7: Commit**

```bash
git add evalkit/tui/widgets/summary_metrics.py tests/tui/test_widgets.py
git commit -m "feat: add summary metrics widget"
```

---

### Task 8: Create Detailed Metrics Table Widget

**Files:**
- Create: `evalkit/tui/widgets/metrics_table.py`
- Modify: `tests/tui/test_widgets.py`

**Step 1: Write failing test**

```python
from evalkit.tui.widgets.metrics_table import MetricsTable


def test_metrics_table():
    """Test detailed metrics table."""
    results = EvaluationResults(
        mode=EvaluationMode.CLASSIFICATION,
        metrics={
            "accuracy": 0.92,
            "macro_avg_precision": 0.91,
        },
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=50,
    )

    table = MetricsTable(results)
    assert table.results == results
```

**Step 2: Run test**

Run: `uv run pytest tests/tui/test_widgets.py::test_metrics_table -v`
Expected: FAIL

**Step 3: Write metrics table widget**

```python
"""Detailed metrics table widget for TUI."""

from textual.widgets import DataTable
from textual.containers import Container

from evalkit.types import EvaluationResults


class MetricsTable(Container):
    """Detailed metrics table widget."""

    def __init__(self, results: EvaluationResults):
        """Initialize metrics table widget."""
        super().__init__()
        self.results = results

    def compose(self):
        """Compose metrics table content."""
        table = DataTable()
        table.add_column("Metric", key="metric")
        table.add_column("Value", key="value")

        # Add rows for each metric
        for key, value in self.results.metrics.items():
            # Skip complex objects
            if isinstance(value, (int, float)):
                formatted_value = f"{value:.4f}" if isinstance(value, float) else str(value)
                table.add_row(key, formatted_value)

        yield table

    DEFAULT_CSS = """
    MetricsTable {
        height: 100%;
        border: solid $primary;
        padding: 1;
    }

    MetricsTable DataTable {
        height: 100%;
    }
    """
```

**Step 4: Run test**

Run: `uv run pytest tests/tui/test_widgets.py::test_metrics_table -v`
Expected: PASS

**Step 5: Commit**

```bash
git add evalkit/tui/widgets/metrics_table.py tests/tui/test_widgets.py
git commit -m "feat: add detailed metrics table widget"
```

---

### Task 9: Create Dashboard Layout

**Files:**
- Create: `evalkit/tui/layouts/dashboard.py`
- Modify: `evalkit/tui/app.py`

**Step 1: Write dashboard layout**

```python
"""Dashboard layout for TUI."""

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static


class DashboardLayout(Container):
    """Grid layout for dashboard."""

    def __init__(self, *children):
        """Initialize dashboard layout."""
        super().__init__(*children)

    DEFAULT_CSS = """
    DashboardLayout {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
        padding: 1;
        height: 100%;
    }

    DashboardLayout > * {
        border: solid $primary;
    }
    """
```

**Step 2: Update layouts __init__.py**

```python
"""Layout configurations for EvalKit TUI."""

from evalkit.tui.layouts.dashboard import DashboardLayout

__all__ = ["DashboardLayout"]
```

**Step 3: Update app.py to use layout**

```python
from evalkit.tui.widgets import Header, Footer, SummaryMetrics, MetricsTable
from evalkit.tui.layouts import DashboardLayout


class EvalKitApp(App):
    # ... existing code ...

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header(self.results, self.filename)

        # Dashboard with 4 panels
        with DashboardLayout():
            yield SummaryMetrics(self.results)
            yield Static("Graph 1")  # Placeholder
            yield MetricsTable(self.results)
            yield Static("Graph 2")  # Placeholder

        yield Footer()
```

**Step 4: Update widgets __init__.py**

```python
from evalkit.tui.widgets.header import Header
from evalkit.tui.widgets.footer import Footer
from evalkit.tui.widgets.summary_metrics import SummaryMetrics
from evalkit.tui.widgets.metrics_table import MetricsTable

__all__ = ["Header", "Footer", "SummaryMetrics", "MetricsTable"]
```

**Step 5: Test manually**

Run: `uv run python cli.py evaluate tests/fixtures/classification_binary.csv --tui`
Expected: Dashboard with 4 panels visible

**Step 6: Commit**

```bash
git add evalkit/tui/layouts/ evalkit/tui/app.py evalkit/tui/widgets/__init__.py
git commit -m "feat: create dashboard grid layout with metrics widgets"
```

---

## Phase 3: Graph Integration

### Task 10: Create Confusion Matrix Widget

**Files:**
- Create: `evalkit/tui/widgets/confusion_matrix.py`
- Modify: `tests/tui/test_widgets.py`

**Step 1: Write failing test**

```python
from evalkit.tui.widgets.confusion_matrix import ConfusionMatrixWidget


def test_confusion_matrix_widget():
    """Test confusion matrix widget."""
    import numpy as np
    results = EvaluationResults(
        mode=EvaluationMode.CLASSIFICATION,
        metrics={
            "confusion_matrix": np.array([[8, 1], [1, 10]]),
            "labels": ["negative", "positive"],
        },
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=20,
    )

    widget = ConfusionMatrixWidget(results)
    assert widget.results == results
```

**Step 2: Run test**

Run: `uv run pytest tests/tui/test_widgets.py::test_confusion_matrix_widget -v`
Expected: FAIL

**Step 3: Write confusion matrix widget**

```python
"""Confusion matrix widget for TUI."""

from textual.widgets import Static
from textual.containers import Container
from rich.table import Table as RichTable

from evalkit.types import EvaluationResults


class ConfusionMatrixWidget(Container):
    """Confusion matrix heatmap widget."""

    def __init__(self, results: EvaluationResults):
        """Initialize confusion matrix widget."""
        super().__init__()
        self.results = results

    def compose(self):
        """Compose confusion matrix content."""
        metrics = self.results.metrics

        if "confusion_matrix" in metrics and "labels" in metrics:
            conf_matrix = metrics["confusion_matrix"]
            labels = metrics["labels"]

            # Create Rich table for confusion matrix
            table = RichTable(title="Confusion Matrix", show_header=True)

            # Add columns
            table.add_column("True \\ Pred", style="cyan")
            for label in labels:
                table.add_column(str(label), justify="center")

            # Add rows
            for i, label in enumerate(labels):
                row = [str(label)]
                for j in range(len(labels)):
                    value = int(conf_matrix[i, j])
                    # Highlight diagonal (correct predictions)
                    if i == j:
                        row.append(f"[green]{value}[/green]")
                    else:
                        row.append(str(value))
                table.add_row(*row)

            yield Static(table)
        else:
            yield Static("No confusion matrix available")

    DEFAULT_CSS = """
    ConfusionMatrixWidget {
        height: 100%;
        padding: 1;
    }
    """
```

**Step 4: Run test**

Run: `uv run pytest tests/tui/test_widgets.py::test_confusion_matrix_widget -v`
Expected: PASS

**Step 5: Commit**

```bash
git add evalkit/tui/widgets/confusion_matrix.py tests/tui/test_widgets.py
git commit -m "feat: add confusion matrix widget"
```

---

### Task 11: Create Graph Panel with Plotext

**Files:**
- Create: `evalkit/tui/widgets/graph_panel.py`
- Modify: `tests/tui/test_widgets.py`

**Step 1: Write failing test**

```python
from evalkit.tui.widgets.graph_panel import ScatterPlot


def test_scatter_plot_widget():
    """Test scatter plot widget."""
    results = EvaluationResults(
        mode=EvaluationMode.REGRESSION,
        metrics={"r2_score": 0.996},
        predicted=np.array([1.0, 2.0, 3.0]),
        gold=np.array([1.1, 2.1, 2.9]),
        sample_count=3,
    )

    widget = ScatterPlot(results)
    assert widget.results == results
```

**Step 2: Run test**

Run: `uv run pytest tests/tui/test_widgets.py::test_scatter_plot_widget -v`
Expected: FAIL

**Step 3: Write scatter plot widget**

```python
"""Graph panel widgets using plotext."""

from textual.widgets import Static
from textual.containers import Container
from textual_plotext import PlotextPlot
import plotext as plt

from evalkit.types import EvaluationResults, EvaluationMode


class ScatterPlot(Container):
    """Scatter plot widget for regression."""

    def __init__(self, results: EvaluationResults):
        """Initialize scatter plot widget."""
        super().__init__()
        self.results = results

    def compose(self):
        """Compose scatter plot content."""
        if self.results.mode != EvaluationMode.REGRESSION:
            yield Static("Scatter plot only for regression")
            return

        def plot_function(plot: plt):
            """Plot function for textual-plotext."""
            y_true = self.results.gold
            y_pred = self.results.predicted

            # Scatter plot
            plot.scatter(y_true, y_pred, marker="dot")

            # Perfect prediction line
            min_val = min(y_true.min(), y_pred.min())
            max_val = max(y_true.max(), y_pred.max())
            plot.plot([min_val, max_val], [min_val, max_val], marker="hd")

            plot.xlabel("Actual Values")
            plot.ylabel("Predicted Values")
            plot.title("Predicted vs Actual")

        yield PlotextPlot(plot_function)

    DEFAULT_CSS = """
    ScatterPlot {
        height: 100%;
        padding: 1;
    }
    """


class BarChart(Container):
    """Bar chart widget for per-class metrics."""

    def __init__(self, results: EvaluationResults):
        """Initialize bar chart widget."""
        super().__init__()
        self.results = results

    def compose(self):
        """Compose bar chart content."""
        if self.results.mode != EvaluationMode.CLASSIFICATION:
            yield Static("Bar chart only for classification")
            return

        metrics = self.results.metrics
        if "per_class" not in metrics:
            yield Static("No per-class metrics available")
            return

        def plot_function(plot: plt):
            """Plot function for textual-plotext."""
            per_class = metrics["per_class"]
            classes = list(per_class.keys())
            precision = [per_class[c]["precision"] for c in classes]
            recall = [per_class[c]["recall"] for c in classes]
            f1 = [per_class[c]["f1_score"] for c in classes]

            # Horizontal bar chart
            y_positions = range(len(classes))
            plot.bar(classes, precision, orientation="h", label="Precision")

            plot.xlabel("Score")
            plot.title("Per-Class Metrics")

        yield PlotextPlot(plot_function)

    DEFAULT_CSS = """
    BarChart {
        height: 100%;
        padding: 1;
    }
    """
```

**Step 4: Run test**

Run: `uv run pytest tests/tui/test_widgets.py::test_scatter_plot_widget -v`
Expected: PASS

**Step 5: Add bar chart test**

```python
from evalkit.tui.widgets.graph_panel import BarChart


def test_bar_chart_widget():
    """Test bar chart widget."""
    results = EvaluationResults(
        mode=EvaluationMode.CLASSIFICATION,
        metrics={
            "per_class": {
                "cat": {"precision": 0.9, "recall": 0.85, "f1_score": 0.87},
                "dog": {"precision": 0.88, "recall": 0.92, "f1_score": 0.90},
            }
        },
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=20,
    )

    widget = BarChart(results)
    assert widget.results == results
```

**Step 6: Run tests**

Run: `uv run pytest tests/tui/test_widgets.py -k "scatter_plot or bar_chart" -v`
Expected: All pass

**Step 7: Commit**

```bash
git add evalkit/tui/widgets/graph_panel.py tests/tui/test_widgets.py
git commit -m "feat: add scatter plot and bar chart widgets with plotext"
```

---

### Task 12: Integrate Graphs into Dashboard

**Files:**
- Modify: `evalkit/tui/app.py`
- Modify: `evalkit/tui/widgets/__init__.py`

**Step 1: Update widgets __init__.py**

```python
from evalkit.tui.widgets.header import Header
from evalkit.tui.widgets.footer import Footer
from evalkit.tui.widgets.summary_metrics import SummaryMetrics
from evalkit.tui.widgets.metrics_table import MetricsTable
from evalkit.tui.widgets.confusion_matrix import ConfusionMatrixWidget
from evalkit.tui.widgets.graph_panel import ScatterPlot, BarChart

__all__ = [
    "Header",
    "Footer",
    "SummaryMetrics",
    "MetricsTable",
    "ConfusionMatrixWidget",
    "ScatterPlot",
    "BarChart",
]
```

**Step 2: Update app.py with graphs**

```python
from evalkit.types import EvaluationMode
from evalkit.tui.widgets import (
    Header,
    Footer,
    SummaryMetrics,
    MetricsTable,
    ConfusionMatrixWidget,
    ScatterPlot,
    BarChart,
)


class EvalKitApp(App):
    # ... existing code ...

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header(self.results, self.filename)

        # Dashboard with appropriate graphs based on mode
        with DashboardLayout():
            yield SummaryMetrics(self.results)

            if self.results.mode == EvaluationMode.CLASSIFICATION:
                yield ConfusionMatrixWidget(self.results)
                yield MetricsTable(self.results)
                yield BarChart(self.results)
            else:  # Regression
                yield ScatterPlot(self.results)
                yield MetricsTable(self.results)
                yield Static("Residual Plot")  # TODO: Next task

        yield Footer()
```

**Step 3: Test with classification**

Run: `uv run python cli.py evaluate tests/fixtures/classification_binary.csv --tui`
Expected: Dashboard with confusion matrix and bar chart

**Step 4: Test with regression**

Run: `uv run python cli.py evaluate tests/fixtures/regression.csv --tui`
Expected: Dashboard with scatter plot

**Step 5: Commit**

```bash
git add evalkit/tui/app.py evalkit/tui/widgets/__init__.py
git commit -m "feat: integrate graphs into dashboard layout"
```

---

## Phase 4: Interactive Features

### Task 13: Add Export Dialog

**Files:**
- Create: `evalkit/tui/widgets/export_dialog.py`
- Modify: `evalkit/tui/app.py`

**Step 1: Write export dialog widget**

```python
"""Export dialog widget for TUI."""

from textual.screen import ModalScreen
from textual.containers import Container, Vertical
from textual.widgets import Button, Label, Input, RadioSet, RadioButton
from textual import on


class ExportDialog(ModalScreen):
    """Modal dialog for exporting results."""

    def __init__(self):
        """Initialize export dialog."""
        super().__init__()
        self.export_path = ""
        self.export_format = "json"

    def compose(self):
        """Compose export dialog."""
        with Container(id="export-dialog"):
            yield Label("Export Evaluation Results")

            yield Label("Format:")
            with RadioSet(id="format-selector"):
                yield RadioButton("JSON", value=True, id="json-radio")
                yield RadioButton("CSV", id="csv-radio")
                yield RadioButton("Markdown", id="md-radio")

            yield Label("Output path:")
            yield Input(placeholder="./evalkit_export.json", id="path-input")

            with Container(id="button-container"):
                yield Button("Export", variant="primary", id="export-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    @on(RadioSet.Changed, "#format-selector")
    def format_changed(self, event: RadioSet.Changed) -> None:
        """Handle format selection change."""
        button_id = event.pressed.id
        if button_id == "json-radio":
            self.export_format = "json"
        elif button_id == "csv-radio":
            self.export_format = "csv"
        elif button_id == "md-radio":
            self.export_format = "md"

    @on(Button.Pressed, "#export-btn")
    def export(self) -> None:
        """Handle export button press."""
        path_input = self.query_one("#path-input", Input)
        self.export_path = path_input.value or f"./evalkit_export.{self.export_format}"
        self.dismiss({"path": self.export_path, "format": self.export_format})

    @on(Button.Pressed, "#cancel-btn")
    def cancel(self) -> None:
        """Handle cancel button press."""
        self.dismiss(None)

    DEFAULT_CSS = """
    ExportDialog {
        align: center middle;
    }

    #export-dialog {
        width: 60;
        height: 20;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    #button-container {
        layout: horizontal;
        height: auto;
        margin-top: 1;
    }

    #button-container Button {
        margin-right: 1;
    }
    """
```

**Step 2: Add export action to app**

In `app.py`:

```python
from evalkit.tui.widgets.export_dialog import ExportDialog
from evalkit.formatters.exporters import export_results


class EvalKitApp(App):
    # ... existing code ...

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("h", "help", "Help"),
        ("?", "help", "Help"),
        ("e", "export", "Export"),
    ]

    def action_export(self) -> None:
        """Show export dialog."""
        def handle_export(result):
            if result:
                try:
                    from pathlib import Path
                    export_results(self.results, Path(result["path"]))
                    self.notify(f"Exported to {result['path']}")
                except Exception as e:
                    self.notify(f"Export failed: {e}", severity="error")

        self.push_screen(ExportDialog(), handle_export)
```

**Step 3: Test export functionality**

Run: `uv run python cli.py evaluate tests/fixtures/classification_binary.csv --tui`
Actions: Press 'e', select format, enter path, click Export
Expected: File created successfully

**Step 4: Commit**

```bash
git add evalkit/tui/widgets/export_dialog.py evalkit/tui/app.py
git commit -m "feat: add export dialog with format selection"
```

---

### Task 14: Add Help Screen

**Files:**
- Create: `evalkit/tui/widgets/help_screen.py`
- Modify: `evalkit/tui/app.py`

**Step 1: Write help screen**

```python
"""Help screen widget for TUI."""

from textual.screen import ModalScreen
from textual.containers import Container, Vertical
from textual.widgets import Static, Button
from textual import on
from rich.table import Table as RichTable


class HelpScreen(ModalScreen):
    """Modal screen showing keyboard shortcuts."""

    def compose(self):
        """Compose help screen."""
        with Container(id="help-screen"):
            yield Static("# EvalKit Keyboard Shortcuts\n", id="help-title")

            # Create shortcuts table
            table = RichTable(show_header=True)
            table.add_column("Key", style="cyan", width=15)
            table.add_column("Action", width=30)

            shortcuts = [
                ("q / Ctrl+C", "Quit application"),
                ("h / ?", "Show this help"),
                ("e", "Export results"),
                ("Tab", "Focus next panel"),
                ("Shift+Tab", "Focus previous panel"),
                ("↑ ↓ ← →", "Navigate/scroll"),
            ]

            for key, action in shortcuts:
                table.add_row(key, action)

            yield Static(table)
            yield Button("Close", variant="primary", id="close-btn")

    @on(Button.Pressed, "#close-btn")
    def close_help(self) -> None:
        """Close help screen."""
        self.dismiss()

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    #help-screen {
        width: 60;
        height: 25;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    #help-title {
        text-align: center;
        margin-bottom: 1;
    }

    #close-btn {
        margin-top: 1;
        width: 100%;
    }
    """
```

**Step 2: Add help action to app**

```python
from evalkit.tui.widgets.help_screen import HelpScreen


class EvalKitApp(App):
    # ... existing code ...

    def action_help(self) -> None:
        """Show help screen."""
        self.push_screen(HelpScreen())
```

**Step 3: Test help screen**

Run: `uv run python cli.py evaluate tests/fixtures/classification_binary.csv --tui`
Actions: Press 'h' or '?'
Expected: Help overlay appears with shortcuts

**Step 4: Commit**

```bash
git add evalkit/tui/widgets/help_screen.py evalkit/tui/app.py
git commit -m "feat: add help screen with keyboard shortcuts"
```

---

## Phase 5: Configuration & Polish

### Task 15: Add Layout Configuration

**Files:**
- Create: `evalkit/tui/config.py`
- Modify: `cli.py`
- Modify: `evalkit/tui/app.py`

**Step 1: Create config module**

```python
"""Configuration for TUI."""

from enum import Enum
from dataclasses import dataclass


class LayoutStyle(Enum):
    """TUI layout styles."""

    MINIMAL = "minimal"
    STANDARD = "standard"
    FULL = "full"


@dataclass
class TUIConfig:
    """TUI configuration."""

    layout: LayoutStyle = LayoutStyle.FULL
    theme: str = "dark"
    show_graphs: bool = True

    @classmethod
    def from_args(cls, layout: str = "full", theme: str = "dark") -> "TUIConfig":
        """Create config from CLI arguments."""
        return cls(
            layout=LayoutStyle(layout),
            theme=theme,
        )
```

**Step 2: Add CLI options**

In `cli.py`, add options:

```python
@click.option(
    "--tui-layout",
    type=click.Choice(["minimal", "standard", "full"]),
    default="full",
    help="TUI layout style",
)
@click.option(
    "--tui-theme",
    type=click.Choice(["dark", "light", "auto"]),
    default="dark",
    help="TUI color theme",
)
def evaluate(csv_file, pred_col, gold_col, mode, output, visualize, viz_dir, no_display, tui, tui_layout, tui_theme):
```

**Step 3: Pass config to app**

```python
        if tui:
            from evalkit.tui import EvalKitApp
            from evalkit.tui.config import TUIConfig
            import os

            filename = os.path.basename(csv_file)
            config = TUIConfig.from_args(tui_layout, tui_theme)
            app = EvalKitApp(results, filename, config)
            app.run()
            sys.exit(0)
```

**Step 4: Update app to use config**

```python
from evalkit.tui.config import TUIConfig, LayoutStyle


class EvalKitApp(App):
    def __init__(
        self,
        results: EvaluationResults,
        filename: str = "predictions.csv",
        config: TUIConfig | None = None,
    ):
        """Initialize app with evaluation results."""
        super().__init__()
        self.results = results
        self.filename = filename
        self.config = config or TUIConfig()

    def compose(self) -> ComposeResult:
        """Compose the UI based on layout config."""
        yield Header(self.results, self.filename)

        if self.config.layout == LayoutStyle.MINIMAL:
            # Minimal layout: just primary graph
            if self.results.mode == EvaluationMode.CLASSIFICATION:
                yield ConfusionMatrixWidget(self.results)
            else:
                yield ScatterPlot(self.results)
        elif self.config.layout == LayoutStyle.STANDARD:
            # Standard layout: metrics + primary graph
            with DashboardLayout():
                yield SummaryMetrics(self.results)
                if self.results.mode == EvaluationMode.CLASSIFICATION:
                    yield ConfusionMatrixWidget(self.results)
                else:
                    yield ScatterPlot(self.results)
                yield MetricsTable(self.results)
                yield Static("")  # Empty panel
        else:  # FULL
            # Full layout: all panels
            with DashboardLayout():
                yield SummaryMetrics(self.results)
                if self.results.mode == EvaluationMode.CLASSIFICATION:
                    yield ConfusionMatrixWidget(self.results)
                    yield MetricsTable(self.results)
                    yield BarChart(self.results)
                else:
                    yield ScatterPlot(self.results)
                    yield MetricsTable(self.results)
                    yield Static("Residual Plot")

        yield Footer()
```

**Step 5: Test different layouts**

Run: `uv run python cli.py evaluate tests/fixtures/classification_binary.csv --tui --tui-layout minimal`
Expected: Only confusion matrix shown

Run: `uv run python cli.py evaluate tests/fixtures/classification_binary.csv --tui --tui-layout standard`
Expected: Metrics + confusion matrix

Run: `uv run python cli.py evaluate tests/fixtures/classification_binary.csv --tui --tui-layout full`
Expected: All panels

**Step 6: Commit**

```bash
git add evalkit/tui/config.py cli.py evalkit/tui/app.py
git commit -m "feat: add configurable layouts (minimal/standard/full)"
```

---

### Task 16: Add Error Handling

**Files:**
- Modify: `evalkit/tui/app.py`
- Create: `evalkit/tui/widgets/error_dialog.py`

**Step 1: Create error dialog**

```python
"""Error dialog for TUI."""

from textual.screen import ModalScreen
from textual.containers import Container
from textual.widgets import Static, Button
from textual import on


class ErrorDialog(ModalScreen):
    """Modal dialog for displaying errors."""

    def __init__(self, title: str, message: str):
        """Initialize error dialog."""
        super().__init__()
        self.title = title
        self.message = message

    def compose(self):
        """Compose error dialog."""
        with Container(id="error-dialog"):
            yield Static(f"[bold red]⚠ {self.title}[/bold red]", id="error-title")
            yield Static(self.message, id="error-message")
            yield Button("OK", variant="error", id="ok-btn")

    @on(Button.Pressed, "#ok-btn")
    def close_dialog(self) -> None:
        """Close error dialog."""
        self.dismiss()

    DEFAULT_CSS = """
    ErrorDialog {
        align: center middle;
    }

    #error-dialog {
        width: 60;
        height: 15;
        background: $surface;
        border: thick $error;
        padding: 2;
    }

    #error-title {
        text-align: center;
        margin-bottom: 1;
    }

    #error-message {
        margin-bottom: 2;
    }

    #ok-btn {
        width: 100%;
    }
    """
```

**Step 2: Add error handling to app**

```python
from evalkit.tui.widgets.error_dialog import ErrorDialog


class EvalKitApp(App):
    # ... existing code ...

    def action_export(self) -> None:
        """Show export dialog."""
        def handle_export(result):
            if result:
                try:
                    from pathlib import Path
                    export_results(self.results, Path(result["path"]))
                    self.notify(f"Exported to {result['path']}", severity="information")
                except Exception as e:
                    self.push_screen(
                        ErrorDialog(
                            "Export Failed",
                            f"Failed to export to {result['path']}\n\nReason: {str(e)}"
                        )
                    )

        self.push_screen(ExportDialog(), handle_export)
```

**Step 3: Test error handling**

Run: `uv run python cli.py evaluate tests/fixtures/classification_binary.csv --tui`
Actions: Press 'e', enter invalid path like "/root/export.json", click Export
Expected: Error dialog appears

**Step 4: Commit**

```bash
git add evalkit/tui/widgets/error_dialog.py evalkit/tui/app.py
git commit -m "feat: add error dialog for user-friendly error display"
```

---

### Task 17: Update Documentation

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`

**Step 1: Update README with TUI section**

Add after CLI Reference section:

```markdown
## 🖥️ Interactive TUI

EvalKit includes a rich Terminal User Interface for interactive exploration:

```bash
# Launch TUI
evalkit evaluate predictions.csv --tui

# Choose layout
evalkit evaluate predictions.csv --tui --tui-layout minimal
evalkit evaluate predictions.csv --tui --tui-layout full
```

**TUI Features:**
- 📊 Dashboard grid layout with multiple panels
- 📈 In-terminal graphs (confusion matrices, scatter plots, bar charts)
- ⌨️ Full keyboard navigation
- 🖱️ Mouse support
- 💾 Export from within TUI
- 🎨 Configurable layouts

**Keyboard Shortcuts:**
- `q` / `Ctrl+C` - Quit
- `h` / `?` - Help
- `e` - Export results
- `Tab` / `Shift+Tab` - Navigate panels
- `↑` `↓` `←` `→` - Scroll

**Layout Options:**
- `--tui-layout minimal` - Primary graph only
- `--tui-layout standard` - Metrics + graphs
- `--tui-layout full` - Complete dashboard (default)
```

**Step 2: Update CLAUDE.md**

Add to Development Commands:

```markdown
### TUI Development
```bash
# Run TUI in development
uv run python cli.py evaluate <file> --tui

# Test different layouts
uv run python cli.py evaluate <file> --tui --tui-layout minimal

# Run TUI tests
uv run pytest tests/tui/ -v
```
```

**Step 3: Commit**

```bash
git add README.md CLAUDE.md
git commit -m "docs: add TUI documentation to README and CLAUDE.md"
```

---

### Task 18: Final Integration Testing

**Files:**
- Create: `tests/tui/test_integration.py`

**Step 1: Write integration tests**

```python
"""Integration tests for TUI."""

import pytest
from evalkit.tui import EvalKitApp
from evalkit import Evaluator, EvaluationMode
from pathlib import Path


@pytest.fixture
def classification_app(tmp_path):
    """Create TUI app with classification data."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    csv_path = fixtures_dir / "classification_binary.csv"

    evaluator = Evaluator.from_csv(csv_path)
    results = evaluator.evaluate()

    return EvalKitApp(results, "test.csv")


@pytest.fixture
def regression_app(tmp_path):
    """Create TUI app with regression data."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    csv_path = fixtures_dir / "regression.csv"

    evaluator = Evaluator.from_csv(csv_path)
    results = evaluator.evaluate()

    return EvalKitApp(results, "test.csv")


def test_app_initializes_classification(classification_app):
    """Test TUI app initializes with classification data."""
    assert classification_app.results.mode == EvaluationMode.CLASSIFICATION
    assert classification_app.filename == "test.csv"


def test_app_initializes_regression(regression_app):
    """Test TUI app initializes with regression data."""
    assert regression_app.results.mode == EvaluationMode.REGRESSION
    assert regression_app.filename == "test.csv"


async def test_app_composes_widgets(classification_app):
    """Test app composes all required widgets."""
    async with classification_app.run_test() as pilot:
        # Check header exists
        assert classification_app.query_one("Header")

        # Check footer exists
        assert classification_app.query_one("Footer")

        # Check dashboard layout
        assert classification_app.query_one("DashboardLayout")
```

**Step 2: Run integration tests**

Run: `uv run pytest tests/tui/test_integration.py -v`
Expected: All tests pass

**Step 3: Run all TUI tests**

Run: `uv run pytest tests/tui/ -v`
Expected: All tests pass

**Step 4: Commit**

```bash
git add tests/tui/test_integration.py
git commit -m "test: add TUI integration tests"
```

---

### Task 19: Final Manual Testing & Polish

**Step 1: Test classification workflow**

Run: `uv run python cli.py evaluate tests/fixtures/classification_binary.csv --tui`
Actions:
- [ ] Verify all panels display correctly
- [ ] Press 'h' to see help
- [ ] Press 'e' to export, save as JSON
- [ ] Navigate with Tab between panels
- [ ] Scroll metrics table with arrow keys
- [ ] Press 'q' to quit

**Step 2: Test regression workflow**

Run: `uv run python cli.py evaluate tests/fixtures/regression.csv --tui`
Actions:
- [ ] Verify scatter plot displays
- [ ] Check metrics are correct
- [ ] Export to CSV
- [ ] Verify all navigation works

**Step 3: Test layout options**

Run each:
- `--tui-layout minimal`
- `--tui-layout standard`
- `--tui-layout full`

Verify correct panels shown for each

**Step 4: Test with large dataset**

Run: `uv run python cli.py evaluate sample_predictions.csv --tui`
Actions:
- [ ] Verify performance is acceptable
- [ ] Scroll through all metrics
- [ ] Verify graphs render correctly

**Step 5: Create final commit**

```bash
git add -A
git commit -m "feat: complete Textual TUI implementation with full features

- Dashboard grid layout with configurable panels
- In-terminal graphs using plotext
- Interactive features (export, help, navigation)
- Full keyboard and mouse support
- Comprehensive test coverage
- Documentation updates

Closes #1"
```

---

## Completion Checklist

- [ ] All dependencies installed
- [ ] TUI module structure created
- [ ] Header and footer widgets working
- [ ] Summary metrics widget displays correctly
- [ ] Detailed metrics table functional
- [ ] Confusion matrix renders properly
- [ ] Scatter plots and bar charts display
- [ ] Dashboard layout configurable
- [ ] Export dialog functional
- [ ] Help screen accessible
- [ ] Layout configuration working (minimal/standard/full)
- [ ] Error handling graceful
- [ ] Documentation updated
- [ ] Integration tests passing
- [ ] Manual testing complete
- [ ] All tests passing: `uv run pytest -v`
- [ ] Code linted: `uv run ruff check .`
- [ ] Code formatted: `uv run ruff format .`
- [ ] Final commit made
- [ ] Issue #1 referenced in commit

---

**Estimated Time:** 6-8 hours for full implementation
**Tests:** 20+ tests covering widgets, layouts, and integration
**Lines of Code:** ~800-1000 new lines
