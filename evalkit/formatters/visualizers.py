"""Visualization generation for evaluation results."""

from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

from evalkit.types import EvaluationResults, EvaluationMode


def generate_visualizations(
    results: EvaluationResults,
    output_dir: str | Path = "./eval_plots",
) -> list[Path]:
    """
    Generate and save visualizations for evaluation results.

    Args:
        results: EvaluationResults object
        output_dir: Directory to save plots

    Returns:
        List of paths to generated plot files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []

    if results.mode == EvaluationMode.CLASSIFICATION:
        saved_files.extend(_generate_classification_plots(results, output_dir))
    else:
        saved_files.extend(_generate_regression_plots(results, output_dir))

    return saved_files


def _generate_classification_plots(results: EvaluationResults, output_dir: Path) -> list[Path]:
    """Generate classification-specific plots."""
    saved_files = []

    # Confusion matrix heatmap
    if "confusion_matrix" in results.metrics:
        fig, ax = plt.subplots(figsize=(10, 8))
        conf_matrix = results.metrics["confusion_matrix"]
        labels = results.metrics.get("labels", [])

        sns.heatmap(
            conf_matrix,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=labels,
            yticklabels=labels,
            ax=ax,
        )
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_title("Confusion Matrix")

        output_path = output_dir / "confusion_matrix.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        saved_files.append(output_path)

    # Per-class metrics bar chart
    if "per_class" in results.metrics and results.metrics["per_class"]:
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        per_class = results.metrics["per_class"]

        classes = list(per_class.keys())
        precision = [per_class[c]["precision"] for c in classes]
        recall = [per_class[c]["recall"] for c in classes]
        f1 = [per_class[c]["f1_score"] for c in classes]

        # Precision
        axes[0].bar(classes, precision, color="steelblue")
        axes[0].set_title("Precision by Class")
        axes[0].set_ylabel("Precision")
        axes[0].set_ylim([0, 1])
        axes[0].tick_params(axis="x", rotation=45)

        # Recall
        axes[1].bar(classes, recall, color="coral")
        axes[1].set_title("Recall by Class")
        axes[1].set_ylabel("Recall")
        axes[1].set_ylim([0, 1])
        axes[1].tick_params(axis="x", rotation=45)

        # F1-Score
        axes[2].bar(classes, f1, color="mediumseagreen")
        axes[2].set_title("F1-Score by Class")
        axes[2].set_ylabel("F1-Score")
        axes[2].set_ylim([0, 1])
        axes[2].tick_params(axis="x", rotation=45)

        output_path = output_dir / "per_class_metrics.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        saved_files.append(output_path)

    return saved_files


def _generate_regression_plots(results: EvaluationResults, output_dir: Path) -> list[Path]:
    """Generate regression-specific plots."""
    saved_files = []

    y_true = results.gold
    y_pred = results.predicted

    # Predicted vs Actual scatter plot
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(y_true, y_pred, alpha=0.5, edgecolors="k", linewidth=0.5)

    # Add diagonal line (perfect predictions)
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], "r--", lw=2, label="Perfect Prediction")

    ax.set_xlabel("Actual Values")
    ax.set_ylabel("Predicted Values")
    ax.set_title(f"Predicted vs Actual (R² = {results.metrics['r2_score']:.2f})")
    ax.legend()
    ax.grid(True, alpha=0.3)

    output_path = output_dir / "predicted_vs_actual.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    saved_files.append(output_path)

    # Residual plot
    if "residuals" in results.metrics:
        residuals = results.metrics["residuals"]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(y_pred, residuals, alpha=0.5, edgecolors="k", linewidth=0.5)
        ax.axhline(y=0, color="r", linestyle="--", lw=2)
        ax.set_xlabel("Predicted Values")
        ax.set_ylabel("Residuals")
        ax.set_title("Residual Plot")
        ax.grid(True, alpha=0.3)

        output_path = output_dir / "residual_plot.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        saved_files.append(output_path)

        # Residual distribution histogram
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(residuals, bins=50, edgecolor="black", alpha=0.7)
        ax.axvline(x=0, color="r", linestyle="--", lw=2)
        ax.set_xlabel("Residual Value")
        ax.set_ylabel("Frequency")
        ax.set_title(
            f"Residual Distribution (μ={results.metrics['mean_residual']:.2f}, "
            f"σ={results.metrics['std_residual']:.2f})"
        )
        ax.grid(True, alpha=0.3, axis="y")

        output_path = output_dir / "residual_distribution.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        saved_files.append(output_path)

    return saved_files
