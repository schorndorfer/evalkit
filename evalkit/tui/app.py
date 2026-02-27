"""Main Textual application for EvalKit TUI."""

from textual.app import App, ComposeResult
from evalkit.types import EvaluationResults


class EvalKitApp(App):
    """EvalKit TUI Application."""

    def __init__(self, results: EvaluationResults):
        """
        Initialize app with evaluation results.

        Args:
            results: Evaluation results to display in the TUI
        """
        super().__init__()
        self.results = results

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield from []  # Empty for now
