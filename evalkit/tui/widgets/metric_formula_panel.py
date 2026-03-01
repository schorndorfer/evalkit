"""Metric formula and calculation display panel."""

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Label
from textual.message import Message

from evalkit.types import EvaluationResults


class MetricFormulaPanel(Container):
    """Panel displaying formula and calculation for selected metric."""

    class MetricSelected(Message):
        """Message sent when a metric is selected."""

        def __init__(self, metric_name: str) -> None:
            """Initialize with selected metric name."""
            super().__init__()
            self.metric_name = metric_name

    def __init__(self, results: EvaluationResults) -> None:
        """
        Initialize metric formula panel.

        Args:
            results: Evaluation results containing metrics
        """
        super().__init__()
        self.results = results
        self.selected_metric = None

    def on_mount(self) -> None:
        """Set border title after mounting."""
        self.border_title = "[bold]Metric Formula[/bold]"

    def compose(self) -> ComposeResult:
        """
        Compose formula panel content.

        Returns:
            Generator yielding content widgets
        """
        with VerticalScroll():
            yield Label("[dim]← Select a metric from the table[/dim]", id="formula-content")

    def update_formula(self, metric_name: str) -> None:
        """
        Update displayed formula for selected metric.

        Args:
            metric_name: Name of the metric to display
        """
        self.selected_metric = metric_name
        self.border_title = f"[bold]{metric_name}[/bold]"

        # Get formula and calculation
        formula_text = self._get_formula_text(metric_name)

        # Update the label
        label = self.query_one("#formula-content", Label)
        label.update(formula_text)

    def _get_formula_text(self, metric_name: str) -> str:
        """
        Generate formula and calculation text for a metric.

        Args:
            metric_name: Name of the metric

        Returns:
            Rich-formatted text with formula and calculation
        """
        metrics = self.results.metrics

        # Handle different metric types
        if metric_name == "Accuracy":
            correct = int(metrics["accuracy"] * self.results.sample_count)
            total = self.results.sample_count
            return (
                f"[cyan bold]Formula:[/cyan bold]\n"
                f"Accuracy = Correct Predictions / Total Predictions\n\n"
                f"[cyan bold]Calculation:[/cyan bold]\n"
                f"Accuracy = {correct} / {total}\n"
                f"Accuracy = [green bold]{metrics['accuracy']:.2f}[/green bold]"
            )

        elif metric_name == "Macro Avg Precision":
            if "per_class" in metrics:
                per_class = metrics["per_class"]
                precisions = [pc["precision"] for pc in per_class.values()]
                precision_str = " + ".join([f"{p:.2f}" for p in precisions])
                return (
                    f"[cyan bold]Formula:[/cyan bold]\n"
                    f"Macro Avg = (Σ Precision per class) / Number of classes\n\n"
                    f"[cyan bold]Calculation:[/cyan bold]\n"
                    f"Macro Avg Precision = ({precision_str}) / {len(precisions)}\n"
                    f"Macro Avg Precision = [green bold]{metrics['macro_avg_precision']:.2f}[/green bold]"
                )
            return "[dim]Not available[/dim]"

        elif metric_name == "Macro Avg Recall":
            if "per_class" in metrics:
                per_class = metrics["per_class"]
                recalls = [pc["recall"] for pc in per_class.values()]
                recall_str = " + ".join([f"{r:.2f}" for r in recalls])
                return (
                    f"[cyan bold]Formula:[/cyan bold]\n"
                    f"Macro Avg = (Σ Recall per class) / Number of classes\n\n"
                    f"[cyan bold]Calculation:[/cyan bold]\n"
                    f"Macro Avg Recall = ({recall_str}) / {len(recalls)}\n"
                    f"Macro Avg Recall = [green bold]{metrics['macro_avg_recall']:.2f}[/green bold]"
                )
            return "[dim]Not available[/dim]"

        elif metric_name == "Macro Avg F1 Score":
            if "per_class" in metrics:
                per_class = metrics["per_class"]
                f1s = [pc["f1_score"] for pc in per_class.values()]
                f1_str = " + ".join([f"{f:.2f}" for f in f1s])
                return (
                    f"[cyan bold]Formula:[/cyan bold]\n"
                    f"Macro Avg = (Σ F1 per class) / Number of classes\n\n"
                    f"[cyan bold]Calculation:[/cyan bold]\n"
                    f"Macro Avg F1 = ({f1_str}) / {len(f1s)}\n"
                    f"Macro Avg F1 = [green bold]{metrics['macro_avg_f1_score']:.2f}[/green bold]"
                )
            return "[dim]Not available[/dim]"

        elif metric_name == "Weighted Avg Precision":
            if "per_class" in metrics:
                per_class = metrics["per_class"]
                items = [(pc["precision"], pc["support"]) for pc in per_class.values()]
                weighted_str = " + ".join([f"({p:.2f} × {s})" for p, s in items])
                total_support = sum(s for _, s in items)
                return (
                    f"[cyan bold]Formula:[/cyan bold]\n"
                    f"Weighted Avg = Σ(Precision × Support) / Total Samples\n\n"
                    f"[cyan bold]Calculation:[/cyan bold]\n"
                    f"Weighted Avg Precision = ({weighted_str}) / {total_support}\n"
                    f"Weighted Avg Precision = [green bold]{metrics['weighted_avg_precision']:.2f}[/green bold]"
                )
            return "[dim]Not available[/dim]"

        elif metric_name == "Weighted Avg Recall":
            if "per_class" in metrics:
                per_class = metrics["per_class"]
                items = [(pc["recall"], pc["support"]) for pc in per_class.values()]
                weighted_str = " + ".join([f"({r:.2f} × {s})" for r, s in items])
                total_support = sum(s for _, s in items)
                return (
                    f"[cyan bold]Formula:[/cyan bold]\n"
                    f"Weighted Avg = Σ(Recall × Support) / Total Samples\n\n"
                    f"[cyan bold]Calculation:[/cyan bold]\n"
                    f"Weighted Avg Recall = ({weighted_str}) / {total_support}\n"
                    f"Weighted Avg Recall = [green bold]{metrics['weighted_avg_recall']:.2f}[/green bold]"
                )
            return "[dim]Not available[/dim]"

        elif metric_name == "Weighted Avg F1 Score":
            if "per_class" in metrics:
                per_class = metrics["per_class"]
                items = [(pc["f1_score"], pc["support"]) for pc in per_class.values()]
                weighted_str = " + ".join([f"({f:.2f} × {s})" for f, s in items])
                total_support = sum(s for _, s in items)
                return (
                    f"[cyan bold]Formula:[/cyan bold]\n"
                    f"Weighted Avg = Σ(F1 × Support) / Total Samples\n\n"
                    f"[cyan bold]Calculation:[/cyan bold]\n"
                    f"Weighted Avg F1 = ({weighted_str}) / {total_support}\n"
                    f"Weighted Avg F1 = [green bold]{metrics['weighted_avg_f1_score']:.2f}[/green bold]"
                )
            return "[dim]Not available[/dim]"

        elif metric_name == "Micro Avg Precision":
            return (
                f"[cyan bold]Formula:[/cyan bold]\n"
                f"Micro Precision = Total TP / (Total TP + Total FP)\n\n"
                f"[cyan bold]Note:[/cyan bold]\n"
                f"Aggregates all true positives and false positives across all classes.\n"
                f"For multi-class: Micro Precision = Accuracy = [green bold]{metrics['micro_avg_precision']:.2f}[/green bold]"
            )

        elif metric_name == "Micro Avg Recall":
            return (
                f"[cyan bold]Formula:[/cyan bold]\n"
                f"Micro Recall = Total TP / (Total TP + Total FN)\n\n"
                f"[cyan bold]Note:[/cyan bold]\n"
                f"Aggregates all true positives and false negatives across all classes.\n"
                f"For multi-class: Micro Recall = Accuracy = [green bold]{metrics['micro_avg_recall']:.2f}[/green bold]"
            )

        elif metric_name == "Micro Avg F1 Score":
            return (
                f"[cyan bold]Formula:[/cyan bold]\n"
                f"Micro F1 = 2 × (Micro Precision × Micro Recall) / (Micro Precision + Micro Recall)\n\n"
                f"[cyan bold]Note:[/cyan bold]\n"
                f"For multi-class classification, Micro F1 equals Accuracy.\n"
                f"Micro F1 = [green bold]{metrics['micro_avg_f1_score']:.2f}[/green bold]"
            )

        elif metric_name == "Sensitivity (Recall)":
            if metrics.get("is_binary"):
                tp = metrics["true_positives"]
                fn = metrics["false_negatives"]
                return (
                    f"[cyan bold]Formula:[/cyan bold]\n"
                    f"Sensitivity = TP / (TP + FN)\n"
                    f"Also known as Recall or True Positive Rate\n\n"
                    f"[cyan bold]Calculation:[/cyan bold]\n"
                    f"Sensitivity = {tp} / ({tp} + {fn})\n"
                    f"Sensitivity = [green bold]{metrics['sensitivity']:.2f}[/green bold]"
                )
            return "[dim]Binary classification only[/dim]"

        elif metric_name == "Specificity":
            if metrics.get("is_binary"):
                tn = metrics["true_negatives"]
                fp = metrics["false_positives"]
                return (
                    f"[cyan bold]Formula:[/cyan bold]\n"
                    f"Specificity = TN / (TN + FP)\n"
                    f"Also known as True Negative Rate\n\n"
                    f"[cyan bold]Calculation:[/cyan bold]\n"
                    f"Specificity = {tn} / ({tn} + {fp})\n"
                    f"Specificity = [green bold]{metrics['specificity']:.2f}[/green bold]"
                )
            return "[dim]Binary classification only[/dim]"

        elif metric_name == "Cohen's Kappa":
            return (
                f"[cyan bold]Formula:[/cyan bold]\n"
                f"κ = (P_o - P_e) / (1 - P_e)\n"
                f"where P_o = observed agreement, P_e = expected agreement by chance\n\n"
                f"[cyan bold]Interpretation:[/cyan bold]\n"
                f"< 0: Poor agreement\n"
                f"0.01-0.20: Slight agreement\n"
                f"0.21-0.40: Fair agreement\n"
                f"0.41-0.60: Moderate agreement\n"
                f"0.61-0.80: Substantial agreement\n"
                f"0.81-1.00: Almost perfect agreement\n\n"
                f"Cohen's Kappa = [green bold]{metrics['cohen_kappa']:.2f}[/green bold]"
            )

        elif metric_name == "Matthews Corrcoef":
            return (
                f"[cyan bold]Formula:[/cyan bold]\n"
                f"MCC = (TP×TN - FP×FN) / √((TP+FP)(TP+FN)(TN+FP)(TN+FN))\n\n"
                f"[cyan bold]Interpretation:[/cyan bold]\n"
                f"+1 = Perfect prediction\n"
                f" 0 = Random prediction\n"
                f"-1 = Perfect inverse prediction\n\n"
                f"Good for imbalanced datasets.\n"
                f"Matthews Correlation Coefficient = [green bold]{metrics['matthews_corrcoef']:.2f}[/green bold]"
            )

        elif metric_name == "R² Score":
            return (
                f"[cyan bold]Formula:[/cyan bold]\n"
                f"R² = 1 - (SS_res / SS_tot)\n"
                f"where SS_res = Σ(y_true - y_pred)², SS_tot = Σ(y_true - ȳ)²\n\n"
                f"[cyan bold]Interpretation:[/cyan bold]\n"
                f"1.0 = Perfect predictions\n"
                f"0.0 = Model performs as well as predicting the mean\n"
                f"< 0 = Model performs worse than predicting the mean\n\n"
                f"R² Score = [green bold]{metrics['r2_score']:.2f}[/green bold]"
            )

        elif metric_name == "MAE":
            return (
                f"[cyan bold]Formula:[/cyan bold]\n"
                f"MAE = (1/n) × Σ|y_true - y_pred|\n\n"
                f"[cyan bold]Interpretation:[/cyan bold]\n"
                f"Average absolute error between predictions and actual values.\n"
                f"Lower is better. Same units as target variable.\n\n"
                f"MAE = [green bold]{metrics['mae']:.2f}[/green bold]"
            )

        elif metric_name == "RMSE":
            return (
                f"[cyan bold]Formula:[/cyan bold]\n"
                f"RMSE = √((1/n) × Σ(y_true - y_pred)²)\n\n"
                f"[cyan bold]Interpretation:[/cyan bold]\n"
                f"Root mean squared error. Penalizes larger errors more than MAE.\n"
                f"Lower is better. Same units as target variable.\n\n"
                f"RMSE = [green bold]{metrics['rmse']:.2f}[/green bold]"
            )

        elif metric_name == "MAPE":
            return (
                f"[cyan bold]Formula:[/cyan bold]\n"
                f"MAPE = (100/n) × Σ|((y_true - y_pred) / y_true)|\n\n"
                f"[cyan bold]Interpretation:[/cyan bold]\n"
                f"Mean absolute percentage error. Scale-independent metric.\n"
                f"Expressed as percentage. Lower is better.\n\n"
                f"MAPE = [green bold]{metrics['mape']:.2f}%[/green bold]"
            )

        # Default fallback
        return f"[dim]Formula not available for {metric_name}[/dim]"

    DEFAULT_CSS = """
    MetricFormulaPanel {
        height: 100%;
        border: round $primary;
        padding: 1;
    }

    MetricFormulaPanel VerticalScroll {
        height: 100%;
    }

    MetricFormulaPanel Label {
        width: 100%;
    }
    """
