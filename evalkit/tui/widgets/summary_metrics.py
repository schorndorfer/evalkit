"""Summary metrics widget for TUI."""

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static

from evalkit.types import EvaluationResults, EvaluationMode


_METRIC_ICONS: dict[str, str] = {
    "Accuracy": "🎯",
    "Precision": "🔍",
    "Recall": "📢",
    "F1-Score": "⚖",
    "Cohen's Kappa": "κ",
    "R² Score": "📈",
    "MAE": "📏",
    "RMSE": "📐",
    "MAPE": "📊",
}


def _get_color(value: float, higher_is_better: bool) -> str:
    """Return a Rich color string based on performance value."""
    if not higher_is_better:
        return "cyan"  # Neutral for lower-is-better / unbounded metrics
    if value >= 0.9:
        return "bright_green"
    elif value >= 0.75:
        return "green"
    elif value >= 0.5:
        return "yellow"
    return "red"


def _progress_bar(value: float, width: int = 10) -> str:
    """Create an ASCII progress bar for values in [0, 1]."""
    filled = round(value * width)
    empty = width - filled
    return f"[dim]▕[/dim]{'█' * filled}{'░' * empty}[dim]▏[/dim]"


class MetricBox(Static):
    """Single metric display box."""

    def __init__(self, label: str, value: float, higher_is_better: bool = True):
        """
        Initialize metric box.

        Args:
            label: Metric label to display
            value: Metric value to display
            higher_is_better: Whether a higher value indicates better performance
        """
        icon = _METRIC_ICONS.get(label, "•")
        color = _get_color(value, higher_is_better)

        if higher_is_better and 0.0 <= value <= 1.0:
            bar = _progress_bar(value)
            content = (
                f"{icon} [bold]{label}[/bold]\n"
                f"[{color} bold]{value:.4f}[/{color} bold]\n"
                f"[{color}]{bar}[/{color}]"
            )
        else:
            content = (
                f"{icon} [bold]{label}[/bold]\n"
                f"[{color} bold]{value:.4f}[/{color} bold]"
            )

        super().__init__(content)

    DEFAULT_CSS = """
    MetricBox {
        border: round $primary;
        padding: 0 1;
        margin: 0 1;
        width: 22;
        height: 6;
    }
    """


class SummaryMetrics(Container):
    """Summary metrics widget showing key metrics."""

    def __init__(self, results: EvaluationResults):
        """
        Initialize summary metrics widget.

        Args:
            results: Evaluation results to display
        """
        super().__init__()
        self.results = results

    def on_mount(self) -> None:
        """Set border title after mounting."""
        self.border_title = "[bold]Key Metrics[/bold]"

    def compose(self) -> ComposeResult:
        """
        Compose summary metrics content.

        Returns:
            Generator yielding metric box widgets
        """
        metrics: dict[str, Any] = self.results.metrics

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
                MetricBox("MAE", metrics.get("mae", 0), higher_is_better=False),
                MetricBox("RMSE", metrics.get("rmse", 0), higher_is_better=False),
            )
            yield Horizontal(
                MetricBox("MAPE", metrics.get("mape", 0), higher_is_better=False),
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
