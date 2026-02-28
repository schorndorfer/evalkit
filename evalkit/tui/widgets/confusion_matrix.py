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

    def on_mount(self) -> None:
        """Set border title after mounting."""
        self.border_title = "[bold]Confusion Matrix[/bold]"

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
            total = int(conf_matrix.sum())

            # Create Rich table for confusion matrix
            table = RichTable(
                title="[bold]Predicted →[/bold]",
                show_header=True,
                header_style="bold cyan",
                border_style="dim",
                show_lines=True,
            )

            # Add columns
            table.add_column("Actual ↓", style="bold cyan", min_width=10)
            for label in labels:
                table.add_column(str(label), justify="center", min_width=12)

            # Add rows with percentage alongside counts
            for i, label in enumerate(labels):
                row = [f"[bold]{label}[/bold]"]
                for j in range(len(labels)):
                    value = int(conf_matrix[i, j])
                    pct = (value / total * 100) if total > 0 else 0.0

                    if i == j:
                        # Diagonal: correct predictions — bright green
                        row.append(f"[bold bright_green]{value}[/bold bright_green] [dim green]({pct:.1f}%)[/dim green]")
                    elif value > 0:
                        # Off-diagonal with misclassifications — red
                        row.append(f"[red]{value}[/red] [dim red]({pct:.1f}%)[/dim red]")
                    else:
                        # Zero misclassifications — dimmed
                        row.append(f"[dim]{value} ({pct:.1f}%)[/dim]")
                table.add_row(*row)

            yield Static(table)
        else:
            yield Static("[dim]No confusion matrix available[/dim]")

    DEFAULT_CSS = """
    ConfusionMatrixWidget {
        height: 100%;
        padding: 1;
    }
    """
