"""Graph panel widgets using plotext."""

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container
from textual_plotext import PlotextPlot

from evalkit.types import EvaluationResults, EvaluationMode


class ScatterPlot(Container):
    """Scatter plot widget for regression."""

    def __init__(self, results: EvaluationResults) -> None:
        """
        Initialize scatter plot widget.

        Args:
            results: Evaluation results containing regression data
        """
        super().__init__()
        self.results = results

    def compose(self) -> ComposeResult:
        """
        Compose scatter plot content.

        Returns:
            Generator yielding PlotextPlot or Static widget
        """
        if self.results.mode != EvaluationMode.REGRESSION:
            yield Static("Scatter plot only for regression")
            return

        yield PlotextPlot()

    def on_mount(self) -> None:
        """Setup plot after widget is mounted."""
        self.border_title = "[bold]Predicted vs Actual[/bold]"

        if self.results.mode != EvaluationMode.REGRESSION:
            return

        plt_widget = self.query_one(PlotextPlot)
        plot = plt_widget.plt

        y_true = self.results.gold
        y_pred = self.results.predicted

        # Scatter plot
        plot.scatter(y_true, y_pred, marker="dot", color="cyan")

        # Perfect prediction line
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        plot.plot([min_val, max_val], [min_val, max_val], marker="hd", color="green", label="Perfect fit")

        plot.xlabel("Actual Values")
        plot.ylabel("Predicted Values")
        plot.title("Predicted vs Actual")

    DEFAULT_CSS = """
    ScatterPlot {
        height: 100%;
        padding: 1;
    }
    """


class BarChart(Container):
    """Bar chart widget for per-class metrics."""

    def __init__(self, results: EvaluationResults) -> None:
        """
        Initialize bar chart widget.

        Args:
            results: Evaluation results containing classification data
        """
        super().__init__()
        self.results = results

    def compose(self) -> ComposeResult:
        """
        Compose bar chart content.

        Returns:
            Generator yielding PlotextPlot or Static widget
        """
        if self.results.mode != EvaluationMode.CLASSIFICATION:
            yield Static("Bar chart only for classification")
            return

        metrics = self.results.metrics
        if "per_class" not in metrics:
            yield Static("No per-class metrics available")
            return

        yield PlotextPlot()

    def on_mount(self) -> None:
        """Setup plot after widget is mounted."""
        self.border_title = "[bold]Per-Class Metrics[/bold]"

        if self.results.mode != EvaluationMode.CLASSIFICATION:
            return

        metrics = self.results.metrics
        if "per_class" not in metrics:
            return

        plt_widget = self.query_one(PlotextPlot)
        plot = plt_widget.plt

        per_class = metrics["per_class"]
        classes = list(per_class.keys())
        precision = [per_class[c]["precision"] for c in classes]
        recall = [per_class[c]["recall"] for c in classes]
        f1 = [per_class[c]["f1_score"] for c in classes]

        # Multiple horizontal bar chart for all three metrics
        plot.multiple_bar(
            classes,
            [precision, recall, f1],
            orientation="h",
            labels=["Precision", "Recall", "F1-Score"],
        )

        plot.xlabel("Score")
        plot.title("Per-Class Metrics")

    DEFAULT_CSS = """
    BarChart {
        height: 100%;
        padding: 1;
    }
    """
