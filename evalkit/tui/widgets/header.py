"""Header widget for TUI."""

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container

from evalkit.types import EvaluationResults, EvaluationMode
from evalkit.tui.utils import get_perf_color, get_perf_label


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
            Generator yielding header Static widgets
        """
        mode = self.results.mode.value.title()
        samples = self.results.sample_count

        # Get top metric based on mode
        if self.results.mode == EvaluationMode.CLASSIFICATION:
            metric_name = "Accuracy"
            metric_val = self.results.metrics.get("accuracy", 0)
            mode_icon = "🔬"
        else:
            metric_name = "R²"
            metric_val = self.results.metrics.get("r2_score", 0)
            mode_icon = "📉"

        color = get_perf_color(metric_val)
        perf = get_perf_label(metric_val)

        title_text = (
            "[bold cyan]⚡ EvalKit[/bold cyan]  [dim]│[/dim]  "
            "[bold]ML Evaluation Dashboard[/bold]"
        )
        info_text = (
            f"{mode_icon} [bold]{mode}[/bold]  [dim]│[/dim]  "
            f"📁 [dim]{self.filename}[/dim]  [dim]│[/dim]  "
            f"📈 [bold]{samples:,}[/bold] samples  [dim]│[/dim]  "
            f"{metric_name}: [bold {color}]{metric_val:.4f}[/bold {color}] [dim]({perf})[/dim]"
        )

        yield Static(title_text, id="header-title")
        yield Static(info_text, id="header-info")

    DEFAULT_CSS = """
    Header {
        height: 5;
        background: $panel;
        border: heavy $primary;
    }

    #header-title {
        text-align: center;
        padding: 1 2 0 2;
    }

    #header-info {
        text-align: center;
        padding: 0 2;
    }
    """
