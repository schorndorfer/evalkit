"""Textual widgets for EvalKit TUI."""

from evalkit.tui.widgets.header import Header
from evalkit.tui.widgets.footer import Footer
from evalkit.tui.widgets.summary_metrics import SummaryMetrics
from evalkit.tui.widgets.metrics_table import MetricsTable
from evalkit.tui.widgets.confusion_matrix import ConfusionMatrixWidget
from evalkit.tui.widgets.graph_panel import ScatterPlot, BarChart
from evalkit.tui.widgets.export_dialog import ExportDialog
from evalkit.tui.widgets.help_screen import HelpScreen

__all__ = [
    "Header",
    "Footer",
    "SummaryMetrics",
    "MetricsTable",
    "ConfusionMatrixWidget",
    "ScatterPlot",
    "BarChart",
    "ExportDialog",
    "HelpScreen",
]
