"""Main Textual application for EvalKit TUI."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Static

from evalkit.types import EvaluationMode, EvaluationResults
from evalkit.tui.config import TUIConfig, LayoutStyle
from evalkit.tui.widgets import (
    Header,
    Footer,
    SummaryMetrics,
    MetricsTable,
    ConfusionMatrixWidget,
    ScatterPlot,
    MetricFormulaPanel,
    ExportDialog,
    HelpScreen,
    ErrorDialog,
)
from evalkit.tui.layouts import DashboardLayout
from evalkit.formatters.exporters import export_results


class EvalKitApp(App):
    """EvalKit TUI Application."""

    TITLE = "EvalKit - ML Evaluation Dashboard"
    CSS_PATH = None
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("h", "help", "Help"),
        ("?", "help", "Help"),
        ("e", "export", "Export"),
    ]

    def __init__(
        self,
        results: EvaluationResults,
        filename: str = "predictions.csv",
        config: TUIConfig | None = None,
    ) -> None:
        """
        Initialize app with evaluation results.

        Args:
            results: Evaluation results to display in the TUI
            filename: Name of the CSV file being evaluated
            config: TUI configuration (layout, theme, etc.)
        """
        super().__init__()
        self.results = results
        self.filename = filename
        self.config = config or TUIConfig()

    def compose(self) -> ComposeResult:
        """
        Compose the UI with layout based on configuration.

        Renders different layouts based on config.layout:
        - MINIMAL: Header + primary graph only
        - STANDARD: Header + 2x2 grid with key widgets
        - FULL: Header + 2x2 grid with all widgets

        Returns:
            Generator yielding UI widgets
        """
        yield Header(self.results, self.filename)

        # Determine primary graph based on mode
        if self.results.mode == EvaluationMode.CLASSIFICATION:
            primary_graph = ConfusionMatrixWidget(self.results)
        else:  # Regression
            primary_graph = ScatterPlot(self.results)

        # Render layout based on config
        if self.config.layout == LayoutStyle.MINIMAL:
            # Minimal layout: Header + primary graph only (no DashboardLayout)
            yield primary_graph
        elif self.config.layout == LayoutStyle.STANDARD:
            # Standard layout: Header + 2x2 grid with key widgets
            with DashboardLayout():
                yield SummaryMetrics(self.results)
                yield primary_graph
                yield MetricsTable(self.results)
                yield Static("")  # Empty panel
        else:  # FULL layout
            # Full layout: Header + 2x2 grid with all widgets
            with DashboardLayout():
                yield SummaryMetrics(self.results)

                if self.results.mode == EvaluationMode.CLASSIFICATION:
                    yield ConfusionMatrixWidget(self.results)
                    yield MetricsTable(self.results)
                    yield MetricFormulaPanel(self.results)
                else:  # Regression
                    yield ScatterPlot(self.results)
                    yield MetricsTable(self.results)
                    yield MetricFormulaPanel(self.results)

        yield Footer()

    def action_help(self) -> None:
        """Show help screen."""
        self.push_screen(HelpScreen())

    def action_export(self) -> None:
        """Show export dialog."""
        def handle_export(result: dict[str, str] | None) -> None:
            """
            Handle export dialog result.

            Args:
                result: Dictionary with 'format' and 'path' keys, or None if cancelled
            """
            if result:
                try:
                    export_results(self.results, Path(result["path"]))
                    self.notify(f"Exported to {result['path']}", severity="information")
                except Exception as e:
                    self.push_screen(
                        ErrorDialog(
                            "Export Failed",
                            f"Failed to export to {result['path']}\n\nReason: {str(e)}"
                        )
                    )

        self.push_screen(ExportDialog(), handle_export)

    def on_metrics_table_metric_selected(self, message: MetricsTable.MetricSelected) -> None:
        """
        Handle metric selection from metrics table.

        Args:
            message: MetricSelected message containing the selected metric name
        """
        # Find the formula panel and update it
        try:
            formula_panel = self.query_one(MetricFormulaPanel)
            formula_panel.update_formula(message.metric_name)
        except Exception:
            # Formula panel not found (might be in minimal/standard layout)
            pass
