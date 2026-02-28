"""Textual widgets for EvalKit TUI."""

from evalkit.tui.widgets.header import Header
from evalkit.tui.widgets.footer import Footer
from evalkit.tui.widgets.summary_metrics import SummaryMetrics
from evalkit.tui.widgets.metrics_table import MetricsTable
from evalkit.tui.widgets.confusion_matrix import ConfusionMatrixWidget
from evalkit.tui.widgets.graph_panel import ScatterPlot, BarChart

__all__ = [
    "Header",
    "Footer",
    "SummaryMetrics",
    "MetricsTable",
    "ConfusionMatrixWidget",
    "ScatterPlot",
    "BarChart",
]
