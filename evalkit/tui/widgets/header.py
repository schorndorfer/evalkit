"""Header widget for TUI."""

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container

from evalkit.types import EvaluationResults, EvaluationMode


class Header(Container):
    """Header widget showing summary information."""

    def __init__(self, results: EvaluationResults, filename: str):
        """
        Initialize header widget.

        Args:
            results: Evaluation results to display
            filename: Name of the CSV file being evaluated
        """
        super().__init__()
        self.results = results
        self.filename = filename

    def compose(self) -> ComposeResult:
        """
        Compose header content.

        Returns:
            Generator yielding header Static widget
        """
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
