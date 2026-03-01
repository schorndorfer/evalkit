"""Detailed metrics table widget for TUI."""

import numpy as np
from rich.text import Text
from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.containers import Container
from textual.message import Message

from evalkit.types import EvaluationResults


_KEY_OVERRIDES: dict[str, str] = {
    "mae": "MAE",
    "rmse": "RMSE",
    "mape": "MAPE",
    "r2_score": "R² Score",
    "cohen_kappa": "Cohen's Kappa",
    "sensitivity": "Sensitivity (Recall)",
    "matthews_corrcoef": "Matthews Corrcoef",
}


def _format_key(key: str) -> str:
    """Convert snake_case metric key to a human-readable Title Case label."""
    return _KEY_OVERRIDES.get(key, key.replace("_", " ").title())


class MetricsTable(Container):
    """Detailed metrics table widget."""

    class MetricSelected(Message):
        """Message emitted when a metric row is selected."""

        def __init__(self, metric_name: str) -> None:
            """Initialize with selected metric name."""
            super().__init__()
            self.metric_name = metric_name

    def __init__(self, results: EvaluationResults) -> None:
        """
        Initialize metrics table widget.

        Args:
            results: Evaluation results to display
        """
        super().__init__()
        self.results = results
        self.metric_keys = []  # Store metric keys in order

    def on_mount(self) -> None:
        """Set border title and trigger initial metric display after mounting."""
        self.border_title = "[bold]All Metrics[/bold]"

        # Trigger display of first metric on startup
        if self.metric_keys:
            first_metric = self.metric_keys[0]
            formatted_name = _format_key(first_metric)
            # Use call_later to ensure the formula panel is ready
            self.call_later(self.post_message, self.MetricSelected(formatted_name))

    def compose(self) -> ComposeResult:
        """
        Compose metrics table content.

        Returns:
            Generator yielding DataTable widget
        """
        table = DataTable(cursor_type="row")
        table.add_column("Metric", key="metric")
        table.add_column("Value", key="value")

        # Add rows for each metric with formatted keys and colored values
        # Skip is_binary as it's not a useful metric to display
        for key, value in self.results.metrics.items():
            if key == "is_binary":
                continue
            if isinstance(value, (int, float, np.number)):
                self.metric_keys.append(key)  # Store original key
                label = Text(_format_key(key), style="bold")
                if not isinstance(value, int):
                    formatted = Text(f"{value:.2f}", style="cyan")
                else:
                    formatted = Text(str(value), style="cyan")
                table.add_row(label, formatted)

        yield table

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """
        Handle row highlighting (cursor movement) in the metrics table.

        Args:
            event: Row highlighted event from DataTable
        """
        # Get the row index and corresponding metric key
        row_index = event.cursor_row
        if 0 <= row_index < len(self.metric_keys):
            metric_key = self.metric_keys[row_index]
            formatted_name = _format_key(metric_key)
            # Post message to parent app
            self.post_message(self.MetricSelected(formatted_name))

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
