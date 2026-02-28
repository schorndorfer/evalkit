"""Summary metrics widget for TUI."""

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static

from evalkit.types import EvaluationResults, EvaluationMode


class MetricBox(Static):
    """Single metric display box."""

    def __init__(self, label: str, value: float):
        """
        Initialize metric box.

        Args:
            label: Metric label to display
            value: Metric value to display
        """
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
        """
        Initialize summary metrics widget.

        Args:
            results: Evaluation results to display
        """
        super().__init__()
        self.results = results

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
                MetricBox("MAE", metrics.get("mae", 0)),
                MetricBox("RMSE", metrics.get("rmse", 0)),
            )
            yield Horizontal(
                MetricBox("MAPE", metrics.get("mape", 0)),
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
