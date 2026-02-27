"""Export evaluation results to various file formats."""

import json
import csv
from pathlib import Path
import numpy as np

from evalkit.types import EvaluationResults, EvaluationMode


def export_results(results: EvaluationResults, output_path: str | Path) -> None:
    """
    Export results to file based on extension.

    Args:
        results: EvaluationResults object
        output_path: Output file path (.json, .csv, or .md)
    """
    output_path = Path(output_path)
    extension = output_path.suffix.lower()

    if extension == ".json":
        export_to_json(results, output_path)
    elif extension == ".csv":
        export_to_csv(results, output_path)
    elif extension == ".md":
        export_to_markdown(results, output_path)
    else:
        raise ValueError(
            f"Unsupported file extension '{extension}'. Supported formats: .json, .csv, .md"
        )


def export_to_json(results: EvaluationResults, output_path: Path) -> None:
    """Export results to JSON format."""

    def convert_numpy(obj):
        """Convert numpy types to Python types for JSON serialization."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(item) for item in obj]
        return obj

    data = {
        "mode": results.mode.value,
        "sample_count": results.sample_count,
        "excluded_count": results.excluded_count,
        "metrics": results.metrics,
    }

    # Convert all numpy types to Python types
    data = convert_numpy(data)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def export_to_csv(results: EvaluationResults, output_path: Path) -> None:
    """Export results to CSV format (key-value pairs)."""
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Mode", results.mode.value])
        writer.writerow(["Sample Count", results.sample_count])
        writer.writerow(["Excluded Count", results.excluded_count])

        # Write main metrics (skip complex objects like confusion matrix)
        for key, value in results.metrics.items():
            if isinstance(value, (int, float, np.number)):
                writer.writerow([key, f"{value:.6f}" if isinstance(value, float) else value])
            elif isinstance(value, str):
                writer.writerow([key, value])
            # Skip arrays, dicts, etc.


def export_to_markdown(results: EvaluationResults, output_path: Path) -> None:
    """Export results to Markdown format."""
    lines = [
        "# Evaluation Results\n",
        f"**Mode:** {results.mode.value.title()}  ",
        f"**Samples:** {results.sample_count}  ",
    ]

    if results.excluded_count > 0:
        lines.append(f"**Excluded:** {results.excluded_count}  ")

    lines.append("")

    # Metrics table
    if results.mode == EvaluationMode.CLASSIFICATION:
        lines.extend(_format_classification_markdown(results.metrics))
    else:
        lines.extend(_format_regression_markdown(results.metrics))

    with open(output_path, "w") as f:
        f.write("\n".join(lines))


def _format_classification_markdown(metrics: dict) -> list[str]:
    """Format classification metrics as markdown tables."""
    lines = ["## Classification Metrics\n", "| Metric | Value |", "|--------|-------|"]

    # Main metrics
    lines.append(f"| Accuracy | {metrics['accuracy']:.4f} |")
    lines.append(f"| Cohen's Kappa | {metrics['cohen_kappa']:.4f} |")
    lines.append(f"| Matthews Corr Coeff | {metrics['matthews_corrcoef']:.4f} |")
    lines.append(f"| Macro Avg Precision | {metrics['macro_avg_precision']:.4f} |")
    lines.append(f"| Macro Avg Recall | {metrics['macro_avg_recall']:.4f} |")
    lines.append(f"| Macro Avg F1-Score | {metrics['macro_avg_f1_score']:.4f} |")

    # Per-class metrics
    if "per_class" in metrics and metrics["per_class"]:
        lines.append("\n## Per-Class Metrics\n")
        lines.append("| Class | Precision | Recall | F1-Score | Support |")
        lines.append("|-------|-----------|--------|----------|---------|")

        for class_label, class_metrics in metrics["per_class"].items():
            lines.append(
                f"| {class_label} | {class_metrics['precision']:.4f} | "
                f"{class_metrics['recall']:.4f} | {class_metrics['f1_score']:.4f} | "
                f"{class_metrics['support']} |"
            )

    return lines


def _format_regression_markdown(metrics: dict) -> list[str]:
    """Format regression metrics as markdown table."""
    lines = ["## Regression Metrics\n", "| Metric | Value |", "|--------|-------|"]

    lines.append(f"| MAE | {metrics['mae']:.4f} |")
    lines.append(f"| MSE | {metrics['mse']:.4f} |")
    lines.append(f"| RMSE | {metrics['rmse']:.4f} |")
    lines.append(f"| R² Score | {metrics['r2_score']:.4f} |")
    lines.append(f"| Adjusted R² | {metrics['adjusted_r2']:.4f} |")

    if metrics.get("mape") is not None:
        lines.append(f"| MAPE | {metrics['mape']:.4f} |")

    lines.append(f"| Median Absolute Error | {metrics['median_absolute_error']:.4f} |")
    lines.append(f"| Max Error | {metrics['max_error']:.4f} |")
    lines.append(f"| Explained Variance | {metrics['explained_variance']:.4f} |")

    return lines
