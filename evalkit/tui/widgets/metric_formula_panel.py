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
            accuracy_pct = metrics["accuracy"] * 100
            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"              [yellow]Correct Predictions[/yellow]\n"
                f"  Accuracy = ──────────────────────\n"
                f"              [yellow]Total Predictions[/yellow]\n\n"
                f"[cyan bold]═══ Calculation ═══[/cyan bold]\n\n"
                f"  Accuracy = [yellow]{correct}[/yellow] / [yellow]{total}[/yellow]\n\n"
                f"           = [green bold]{metrics['accuracy']:.2f}[/green bold]  ([green bold]{accuracy_pct:.1f}%[/green bold])"
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

        elif metric_name == "True Positives":
            if metrics.get("is_binary"):
                tp = metrics["true_positives"]
                tn = metrics["true_negatives"]
                fp = metrics["false_positives"]
                fn = metrics["false_negatives"]
                return self._confusion_matrix_display(tp, tn, fp, fn, "True Positives")
            return "[dim]Binary classification only[/dim]"

        elif metric_name == "True Negatives":
            if metrics.get("is_binary"):
                tp = metrics["true_positives"]
                tn = metrics["true_negatives"]
                fp = metrics["false_positives"]
                fn = metrics["false_negatives"]
                return self._confusion_matrix_display(tp, tn, fp, fn, "True Negatives")
            return "[dim]Binary classification only[/dim]"

        elif metric_name == "False Positives":
            if metrics.get("is_binary"):
                tp = metrics["true_positives"]
                tn = metrics["true_negatives"]
                fp = metrics["false_positives"]
                fn = metrics["false_negatives"]
                return self._confusion_matrix_display(tp, tn, fp, fn, "False Positives")
            return "[dim]Binary classification only[/dim]"

        elif metric_name == "False Negatives":
            if metrics.get("is_binary"):
                tp = metrics["true_positives"]
                tn = metrics["true_negatives"]
                fp = metrics["false_positives"]
                fn = metrics["false_negatives"]
                return self._confusion_matrix_display(tp, tn, fp, fn, "False Negatives")
            return "[dim]Binary classification only[/dim]"

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
            kappa_val = metrics['cohen_kappa']
            # Determine interpretation level
            if kappa_val < 0:
                level = "[red]Poor agreement[/red]"
            elif kappa_val < 0.21:
                level = "[yellow]Slight agreement[/yellow]"
            elif kappa_val < 0.41:
                level = "[yellow]Fair agreement[/yellow]"
            elif kappa_val < 0.61:
                level = "[cyan]Moderate agreement[/cyan]"
            elif kappa_val < 0.81:
                level = "[green]Substantial agreement[/green]"
            else:
                level = "[green bold]Almost perfect agreement[/green bold]"

            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"         [yellow]P_o[/yellow] - [yellow]P_e[/yellow]\n"
                f"    κ = ─────────\n"
                f"         1 - [yellow]P_e[/yellow]\n\n"
                f"  where:\n"
                f"    [yellow]P_o[/yellow] = observed agreement\n"
                f"    [yellow]P_e[/yellow] = expected agreement by chance\n\n"
                f"[cyan bold]═══ Interpretation Guide ═══[/cyan bold]\n\n"
                f"  [dim]< 0.00[/dim]     Poor agreement\n"
                f"  [dim]0.01-0.20[/dim]  Slight agreement\n"
                f"  [dim]0.21-0.40[/dim]  Fair agreement\n"
                f"  [dim]0.41-0.60[/dim]  Moderate agreement\n"
                f"  [dim]0.61-0.80[/dim]  Substantial agreement\n"
                f"  [dim]0.81-1.00[/dim]  Almost perfect agreement\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  κ = [green bold]{kappa_val:.2f}[/green bold]  ({level})"
            )

        elif metric_name == "Matthews Corrcoef":
            mcc_val = metrics['matthews_corrcoef']
            if mcc_val > 0.7:
                level = "[green bold]Strong positive correlation[/green bold]"
            elif mcc_val > 0.3:
                level = "[green]Moderate positive correlation[/green]"
            elif mcc_val > -0.3:
                level = "[yellow]Weak or no correlation[/yellow]"
            else:
                level = "[red]Negative correlation[/red]"

            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"         [yellow]TP[/yellow]×[yellow]TN[/yellow] - [yellow]FP[/yellow]×[yellow]FN[/yellow]\n"
                f"  MCC = ─────────────────────────────\n"
                f"        √([yellow]TP[/yellow]+[yellow]FP[/yellow])([yellow]TP[/yellow]+[yellow]FN[/yellow])([yellow]TN[/yellow]+[yellow]FP[/yellow])([yellow]TN[/yellow]+[yellow]FN[/yellow])\n\n"
                f"[cyan bold]═══ Interpretation Guide ═══[/cyan bold]\n\n"
                f"  [green]+1[/green]  Perfect prediction\n"
                f"  [dim] 0[/dim]  Random prediction\n"
                f"  [red]-1[/red]  Perfect inverse prediction\n\n"
                f"  [dim italic]Good for imbalanced datasets[/dim italic]\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  MCC = [green bold]{mcc_val:.2f}[/green bold]  ({level})"
            )

        elif metric_name == "R² Score":
            r2_val = metrics['r2_score']
            if r2_val > 0.9:
                level = "[green bold]Excellent fit[/green bold]"
            elif r2_val > 0.7:
                level = "[green]Good fit[/green]"
            elif r2_val > 0.5:
                level = "[yellow]Moderate fit[/yellow]"
            elif r2_val > 0:
                level = "[yellow]Weak fit[/yellow]"
            else:
                level = "[red]Poor fit (worse than mean)[/red]"

            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"           [yellow]SS_res[/yellow]\n"
                f"  R² = 1 - ────────\n"
                f"           [yellow]SS_tot[/yellow]\n\n"
                f"  where:\n"
                f"    [yellow]SS_res[/yellow] = Σ([blue]y_true[/blue] - [green]y_pred[/green])²  [dim](residual sum of squares)[/dim]\n"
                f"    [yellow]SS_tot[/yellow] = Σ([blue]y_true[/blue] - [blue]ȳ[/blue])²       [dim](total sum of squares)[/dim]\n\n"
                f"[cyan bold]═══ Interpretation Guide ═══[/cyan bold]\n\n"
                f"  [green]1.0[/green]   Perfect predictions\n"
                f"  [dim]0.0[/dim]   Same as predicting the mean\n"
                f"  [red]< 0[/red]   Worse than predicting the mean\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  R² = [green bold]{r2_val:.2f}[/green bold]  ({level})"
            )

        elif metric_name == "MAE":
            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"         1\n"
                f"  MAE = ─ × Σ |[blue]y_true[/blue] - [green]y_pred[/green]|\n"
                f"         [yellow]n[/yellow]\n\n"
                f"[cyan bold]═══ Interpretation ═══[/cyan bold]\n\n"
                f"  Mean Absolute Error\n"
                f"  • Average distance between predictions and actual values\n"
                f"  • Same units as target variable\n"
                f"  • [green]Lower is better[/green]\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  MAE = [green bold]{metrics['mae']:.2f}[/green bold]"
            )

        elif metric_name == "MSE":
            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"         1\n"
                f"  MSE = ─ × Σ([blue]y_true[/blue] - [green]y_pred[/green])²\n"
                f"         [yellow]n[/yellow]\n\n"
                f"[cyan bold]═══ Interpretation ═══[/cyan bold]\n\n"
                f"  Mean Squared Error\n"
                f"  • Squares errors, heavily penalizing large deviations\n"
                f"  • Units are squared (not directly interpretable)\n"
                f"  • [green]Lower is better[/green]\n"
                f"  • RMSE = √MSE gives same units as target\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  MSE = [green bold]{metrics['mse']:.2f}[/green bold]"
            )

        elif metric_name == "RMSE":
            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"           ┌──────────────────────\n"
                f"           │  1\n"
                f"  RMSE = ╲ │  ─ × Σ([blue]y_true[/blue] - [green]y_pred[/green])²\n"
                f"          ╲│  [yellow]n[/yellow]\n\n"
                f"[cyan bold]═══ Interpretation ═══[/cyan bold]\n\n"
                f"  Root Mean Squared Error\n"
                f"  • Penalizes larger errors more than MAE\n"
                f"  • Same units as target variable\n"
                f"  • [green]Lower is better[/green]\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  RMSE = [green bold]{metrics['rmse']:.2f}[/green bold]"
            )

        elif metric_name == "MAPE":
            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"          100      │ [blue]y_true[/blue] - [green]y_pred[/green] │\n"
                f"  MAPE = ───── × Σ │ ──────────────── │\n"
                f"           [yellow]n[/yellow]       │     [blue]y_true[/blue]      │\n\n"
                f"[cyan bold]═══ Interpretation ═══[/cyan bold]\n\n"
                f"  Mean Absolute Percentage Error\n"
                f"  • Scale-independent metric (works across different scales)\n"
                f"  • Expressed as percentage\n"
                f"  • [green]Lower is better[/green]\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  MAPE = [green bold]{metrics['mape']:.2f}%[/green bold]"
            )

        elif metric_name == "Adjusted R²":
            adj_r2_val = metrics['adjusted_r2']
            r2_val = metrics['r2_score']
            n = self.results.sample_count
            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"                    ([yellow]n[/yellow] - 1)\n"
                f"  Adj R² = 1 - (1 - R²) × ─────────\n"
                f"                    ([yellow]n[/yellow] - [yellow]p[/yellow] - 1)\n\n"
                f"  where:\n"
                f"    [yellow]n[/yellow] = number of samples = {n}\n"
                f"    [yellow]p[/yellow] = number of predictors = 1\n"
                f"    R² = {r2_val:.2f}\n\n"
                f"[cyan bold]═══ Interpretation ═══[/cyan bold]\n\n"
                f"  Adjusted R² Score\n"
                f"  • R² adjusted for number of predictors\n"
                f"  • Penalizes adding unnecessary predictors\n"
                f"  • More reliable for model comparison\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  Adjusted R² = [green bold]{adj_r2_val:.2f}[/green bold]"
            )

        elif metric_name == "Median Absolute Error":
            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"  MedAE = median(|[blue]y_true[/blue] - [green]y_pred[/green]|)\n\n"
                f"[cyan bold]═══ Interpretation ═══[/cyan bold]\n\n"
                f"  Median Absolute Error\n"
                f"  • Robust to outliers (unlike MAE/MSE)\n"
                f"  • 50th percentile of absolute errors\n"
                f"  • Same units as target variable\n"
                f"  • [green]Lower is better[/green]\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  MedAE = [green bold]{metrics['median_absolute_error']:.2f}[/green bold]"
            )

        elif metric_name == "Max Error":
            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"  Max Error = max(|[blue]y_true[/blue] - [green]y_pred[/green]|)\n\n"
                f"[cyan bold]═══ Interpretation ═══[/cyan bold]\n\n"
                f"  Maximum Error (Worst-Case)\n"
                f"  • Largest absolute error in predictions\n"
                f"  • Useful for understanding worst-case performance\n"
                f"  • Same units as target variable\n"
                f"  • [green]Lower is better[/green]\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  Max Error = [green bold]{metrics['max_error']:.2f}[/green bold]"
            )

        elif metric_name == "Explained Variance":
            ev_val = metrics['explained_variance']
            if ev_val > 0.9:
                level = "[green bold]Excellent[/green bold]"
            elif ev_val > 0.7:
                level = "[green]Good[/green]"
            elif ev_val > 0.5:
                level = "[yellow]Moderate[/yellow]"
            else:
                level = "[yellow]Weak[/yellow]"

            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"           Var([blue]y_true[/blue] - [green]y_pred[/green])\n"
                f"  EV = 1 - ───────────────────\n"
                f"                Var([blue]y_true[/blue])\n\n"
                f"[cyan bold]═══ Interpretation ═══[/cyan bold]\n\n"
                f"  Explained Variance Score\n"
                f"  • Proportion of variance explained by model\n"
                f"  • Similar to R² but without squared terms\n"
                f"  • Range: (-∞, 1], best = 1\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  EV = [green bold]{ev_val:.2f}[/green bold]  ({level})"
            )

        elif metric_name == "Mean Residual":
            mean_res = metrics['mean_residual']
            if abs(mean_res) < 0.01 * abs(self.results.gold.mean()):
                level = "[green]Near zero (unbiased)[/green]"
            elif mean_res > 0:
                level = "[yellow]Positive bias (over-predicting)[/yellow]"
            else:
                level = "[yellow]Negative bias (under-predicting)[/yellow]"

            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"             1\n"
                f"  Mean Res = ─ × Σ([blue]y_true[/blue] - [green]y_pred[/green])\n"
                f"             [yellow]n[/yellow]\n\n"
                f"[cyan bold]═══ Interpretation ═══[/cyan bold]\n\n"
                f"  Mean Residual (Bias)\n"
                f"  • Average difference between actual and predicted\n"
                f"  • Should be close to 0 for unbiased models\n"
                f"  • Positive = model under-predicts on average\n"
                f"  • Negative = model over-predicts on average\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  Mean Residual = [green bold]{mean_res:.2f}[/green bold]  ({level})"
            )

        elif metric_name == "Std Residual":
            return (
                f"[cyan bold]═══ Formula ═══[/cyan bold]\n\n"
                f"            ┌──────────────────────────\n"
                f"            │  1\n"
                f"  Std Res = ╲ │  ─ × Σ(residual - μ)²\n"
                f"             ╲│  [yellow]n[/yellow]\n\n"
                f"  where residual = [blue]y_true[/blue] - [green]y_pred[/green]\n\n"
                f"[cyan bold]═══ Interpretation ═══[/cyan bold]\n\n"
                f"  Standard Deviation of Residuals\n"
                f"  • Spread/variability of prediction errors\n"
                f"  • Same units as target variable\n"
                f"  • [green]Lower is better[/green] (more consistent predictions)\n\n"
                f"[cyan bold]═══ Result ═══[/cyan bold]\n\n"
                f"  Std Residual = [green bold]{metrics['std_residual']:.2f}[/green bold]"
            )

        # Default fallback
        return f"[dim]Formula not available for {metric_name}[/dim]"

    def _confusion_matrix_display(
        self, tp: int, tn: int, fp: int, fn: int, highlight_metric: str
    ) -> str:
        """
        Generate confusion matrix visualization with highlighted metric.

        Args:
            tp: True positives
            tn: True negatives
            fp: False positives
            fn: False negatives
            highlight_metric: Which metric to highlight

        Returns:
            Rich-formatted confusion matrix display
        """
        # Highlight styles based on which metric is selected
        tp_style = "[yellow bold on blue]" if highlight_metric == "True Positives" else "[green]"
        tn_style = "[yellow bold on blue]" if highlight_metric == "True Negatives" else "[green]"
        fp_style = "[yellow bold on red]" if highlight_metric == "False Positives" else "[red]"
        fn_style = "[yellow bold on red]" if highlight_metric == "False Negatives" else "[red]"

        total = tp + tn + fp + fn

        return (
            f"[cyan bold]Confusion Matrix:[/cyan bold]\n\n"
            f"                 Predicted\n"
            f"              Pos       Neg\n"
            f"         ┌─────────┬─────────┐\n"
            f"    Pos  │ {tp_style}{tp:^7}[/] │ {fn_style}{fn:^7}[/] │\n"
            f"Actual   │   TP    │   FN    │\n"
            f"         ├─────────┼─────────┤\n"
            f"    Neg  │ {fp_style}{fp:^7}[/] │ {tn_style}{tn:^7}[/] │\n"
            f"         │   FP    │   TN    │\n"
            f"         └─────────┴─────────┘\n\n"
            f"[cyan bold]Breakdown:[/cyan bold]\n"
            f"{tp_style}True Positives (TP)[/]:  {tp} ({tp/total*100:.1f}%)\n"
            f"{tn_style}True Negatives (TN)[/]:  {tn} ({tn/total*100:.1f}%)\n"
            f"{fp_style}False Positives (FP)[/]: {fp} ({fp/total*100:.1f}%)\n"
            f"{fn_style}False Negatives (FN)[/]: {fn} ({fn/total*100:.1f}%)\n"
        )

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
