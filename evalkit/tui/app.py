"""Main Textual application for EvalKit TUI."""

from textual.app import App, ComposeResult
from textual.widgets import Static

from evalkit.types import EvaluationResults
from evalkit.tui.widgets import Header, Footer, SummaryMetrics, MetricsTable
from evalkit.tui.layouts import DashboardLayout


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
        """
        Initialize app with evaluation results.

        Args:
            results: Evaluation results to display in the TUI
            filename: Name of the CSV file being evaluated
        """
        super().__init__()
        self.results = results
        self.filename = filename

    def compose(self) -> ComposeResult:
        """
        Compose the UI.

        Returns:
            Generator yielding UI widgets
        """
        yield Header(self.results, self.filename)

        # Dashboard with 4 panels
        with DashboardLayout():
            yield SummaryMetrics(self.results)
            yield Static("Graph 1")  # Placeholder
            yield MetricsTable(self.results)
            yield Static("Graph 2")  # Placeholder

        yield Footer()

    def action_help(self) -> None:
        """Show help screen."""
        self.bell()  # Placeholder
