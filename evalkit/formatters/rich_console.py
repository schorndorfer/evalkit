"""Rich terminal formatting for evaluation results."""

import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from evalkit.types import EvaluationResults, EvaluationMode


def display_results(results: EvaluationResults, console: Console | None = None) -> None:
    """
    Display evaluation results in rich terminal format.

    Args:
        results: EvaluationResults object
        console: Rich console (creates new one if None)
    """
    if console is None:
        console = Console()

    # Header panel
    header = Panel(
        f"[bold]Evaluation Results[/bold]\n"
        f"Mode: {results.mode.value.title()}\n"
        f"Samples: {results.sample_count}"
        + (
            f"\n[yellow]Excluded: {results.excluded_count}[/yellow]"
            if results.excluded_count > 0
            else ""
        ),
        border_style="cyan",
    )
    console.print(header)
    console.print()

    # Display metrics based on mode
    if results.mode == EvaluationMode.CLASSIFICATION:
        _display_classification_metrics(results, console)
    else:
        _display_regression_metrics(results, console)


def _display_classification_metrics(results: EvaluationResults, console: Console) -> None:
    """Display classification metrics."""
    metrics = results.metrics

    # Main metrics table
    table = Table(title="Classification Metrics", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", justify="right", style="green")

    # Overall metrics
    table.add_row("Accuracy", f"{metrics['accuracy']:.4f}")
    table.add_row("Cohen's Kappa", f"{metrics['cohen_kappa']:.4f}")
    table.add_row("Matthews Corr Coeff", f"{metrics['matthews_corrcoef']:.4f}")

    # Separator
    table.add_section()

    # Macro averages
    table.add_row("Macro Avg Precision", f"{metrics['macro_avg_precision']:.4f}")
    table.add_row("Macro Avg Recall", f"{metrics['macro_avg_recall']:.4f}")
    table.add_row("Macro Avg F1-Score", f"{metrics['macro_avg_f1_score']:.4f}")

    # Separator
    table.add_section()

    # Weighted averages
    table.add_row("Weighted Avg Precision", f"{metrics['weighted_avg_precision']:.4f}")
    table.add_row("Weighted Avg Recall", f"{metrics['weighted_avg_recall']:.4f}")
    table.add_row("Weighted Avg F1-Score", f"{metrics['weighted_avg_f1_score']:.4f}")

    # Binary classification specifics
    if metrics.get("is_binary", False):
        table.add_section()
        table.add_row("Sensitivity (Recall)", f"{metrics['sensitivity']:.4f}")
        table.add_row("Specificity", f"{metrics['specificity']:.4f}")
        table.add_row("True Positives", str(metrics["true_positives"]))
        table.add_row("True Negatives", str(metrics["true_negatives"]))
        table.add_row("False Positives", str(metrics["false_positives"]))
        table.add_row("False Negatives", str(metrics["false_negatives"]))

    console.print(table)
    console.print()

    # Per-class metrics
    if "per_class" in metrics and metrics["per_class"]:
        class_table = Table(
            title="Per-Class Metrics", show_header=True, header_style="bold magenta"
        )
        class_table.add_column("Class", style="cyan")
        class_table.add_column("Precision", justify="right")
        class_table.add_column("Recall", justify="right")
        class_table.add_column("F1-Score", justify="right")
        class_table.add_column("Support", justify="right", style="dim")

        for class_label, class_metrics in metrics["per_class"].items():
            class_table.add_row(
                str(class_label),
                f"{class_metrics['precision']:.4f}",
                f"{class_metrics['recall']:.4f}",
                f"{class_metrics['f1_score']:.4f}",
                str(class_metrics["support"]),
            )

        console.print(class_table)
        console.print()

    # Confusion matrix
    if "confusion_matrix" in metrics:
        _display_confusion_matrix(metrics["confusion_matrix"], metrics.get("labels", []), console)


def _display_regression_metrics(results: EvaluationResults, console: Console) -> None:
    """Display regression metrics."""
    metrics = results.metrics

    # Main metrics table
    table = Table(title="Regression Metrics", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", justify="right", style="green")

    # Error metrics
    table.add_row("MAE (Mean Absolute Error)", f"{metrics['mae']:.4f}")
    table.add_row("MSE (Mean Squared Error)", f"{metrics['mse']:.4f}")
    table.add_row("RMSE (Root Mean Squared Error)", f"{metrics['rmse']:.4f}")
    table.add_row("Median Absolute Error", f"{metrics['median_absolute_error']:.4f}")
    table.add_row("Max Error", f"{metrics['max_error']:.4f}")

    if metrics.get("mape") is not None:
        table.add_row("MAPE (Mean Absolute % Error)", f"{metrics['mape']:.4f}")

    # Separator
    table.add_section()

    # Score metrics
    table.add_row("R² Score", f"{metrics['r2_score']:.4f}")
    table.add_row("Adjusted R²", f"{metrics['adjusted_r2']:.4f}")
    table.add_row("Explained Variance", f"{metrics['explained_variance']:.4f}")

    # Separator
    table.add_section()

    # Residual statistics
    table.add_row("Mean Residual", f"{metrics['mean_residual']:.4f}")
    table.add_row("Std Residual", f"{metrics['std_residual']:.4f}")

    console.print(table)
    console.print()


def _display_confusion_matrix(conf_matrix: np.ndarray, labels: list, console: Console) -> None:
    """Display confusion matrix as a table."""
    table = Table(title="Confusion Matrix", show_header=True, header_style="bold magenta")

    # Add columns
    table.add_column("True \\ Pred", style="cyan")
    for label in labels:
        table.add_column(str(label), justify="center")

    # Add rows
    for i, label in enumerate(labels):
        row = [str(label)]
        for j in range(len(labels)):
            value = int(conf_matrix[i, j])
            # Highlight diagonal (correct predictions) in green
            if i == j:
                row.append(f"[green]{value}[/green]")
            else:
                row.append(str(value))
        table.add_row(*row)

    console.print(table)
    console.print()
