"""Confusion matrix widget for TUI."""

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container
from rich.table import Table as RichTable

from evalkit.types import EvaluationResults


class ConfusionMatrixWidget(Container):
    """Confusion matrix heatmap widget."""

    def __init__(self, results: EvaluationResults) -> None:
        """
        Initialize confusion matrix widget.

        Args:
            results: Evaluation results containing confusion matrix
        """
        super().__init__()
        self.results = results

    def compose(self) -> ComposeResult:
        """
        Compose confusion matrix content.

        Returns:
            Generator yielding Static widget with confusion matrix table
        """
        metrics = self.results.metrics

        if "confusion_matrix" in metrics and "labels" in metrics:
            conf_matrix = metrics["confusion_matrix"]
            labels = metrics["labels"]

            # Create Rich table for confusion matrix
            table = RichTable(title="Confusion Matrix", show_header=True)

            # Add columns
            table.add_column("True \\ Pred", style="cyan")
            for label in labels:
                table.add_column(str(label), justify="center")

            # Add rows
            for i, label in enumerate(labels):
                row = [str(label)]
                for j in range(len(labels)):
                    value = int(conf_matrix[i, j])
                    # Highlight diagonal (correct predictions)
                    if i == j:
                        row.append(f"[green]{value}[/green]")
                    else:
                        row.append(str(value))
                table.add_row(*row)

            yield Static(table)
        else:
            yield Static("No confusion matrix available")

    DEFAULT_CSS = """
    ConfusionMatrixWidget {
        height: 100%;
        padding: 1;
    }
    """
