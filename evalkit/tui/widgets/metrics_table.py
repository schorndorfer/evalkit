"""Detailed metrics table widget for TUI."""

import numpy as np
from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.containers import Container

from evalkit.types import EvaluationResults


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

    def compose(self) -> ComposeResult:
        """
        Compose metrics table content.

        Returns:
            Generator yielding DataTable widget
        """
        table = DataTable()
        table.add_column("Metric", key="metric")
        table.add_column("Value", key="value")

        # Add rows for each metric
        for key, value in self.results.metrics.items():
            # Skip complex objects
            if isinstance(value, (int, float, np.number)):
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
