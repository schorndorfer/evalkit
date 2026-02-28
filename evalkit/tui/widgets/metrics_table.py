"""Detailed metrics table widget for TUI."""

import numpy as np
from rich.text import Text
from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.containers import Container

from evalkit.types import EvaluationResults


_KEY_OVERRIDES: dict[str, str] = {
    "mae": "MAE",
    "rmse": "RMSE",
    "mape": "MAPE",
    "r2_score": "R² Score",
    "cohen_kappa": "Cohen's Kappa",
}


def _format_key(key: str) -> str:
    """Convert snake_case metric key to a human-readable Title Case label."""
    return _KEY_OVERRIDES.get(key, key.replace("_", " ").title())


class MetricsTable(Container):
    """Detailed metrics table widget."""

    def __init__(self, results: EvaluationResults) -> None:
        """
        Initialize metrics table widget.

        Args:
            results: Evaluation results to display
        """
        super().__init__()
        self.results = results

    def on_mount(self) -> None:
        """Set border title after mounting."""
        self.border_title = "[bold]All Metrics[/bold]"

    def compose(self) -> ComposeResult:
        """
        Compose metrics table content.

        Returns:
            Generator yielding DataTable widget
        """
        table = DataTable()
        table.add_column("Metric", key="metric")
        table.add_column("Value", key="value")

        # Add rows for each metric with formatted keys and colored values
        for key, value in self.results.metrics.items():
            if isinstance(value, (int, float, np.number)):
                label = Text(_format_key(key), style="bold")
                if not isinstance(value, int):
                    formatted = Text(f"{value:.2f}", style="cyan")
                else:
                    formatted = Text(str(value), style="cyan")
                table.add_row(label, formatted)

        yield table

    DEFAULT_CSS = """
    MetricsTable {
        height: 100%;
        border: round $primary;
        padding: 1;
    }

    MetricsTable DataTable {
        height: 100%;
    }
    """
