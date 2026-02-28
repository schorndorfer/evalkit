"""Tests for TUI widgets."""

from evalkit.tui.widgets.header import Header
from evalkit.tui.widgets.footer import Footer
from evalkit.tui.widgets.summary_metrics import SummaryMetrics
from evalkit.tui.widgets.metrics_table import MetricsTable
from evalkit.tui.widgets.confusion_matrix import ConfusionMatrixWidget
from evalkit.types import EvaluationResults, EvaluationMode
from textual.widgets import Footer as TextualFooter
import numpy as np


def test_header_widget_classification():
    """Test header widget with classification results."""
    results = EvaluationResults(
        mode=EvaluationMode.CLASSIFICATION,
        metrics={"accuracy": 0.92},
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=50,
        excluded_count=0,
    )

    header = Header(results, "test.csv")
    assert header.results == results
    assert header.filename == "test.csv"


def test_header_widget_regression():
    """Test header widget with regression results."""
    results = EvaluationResults(
        mode=EvaluationMode.REGRESSION,
        metrics={"r2_score": 0.996},
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=20,
        excluded_count=0,
    )

    header = Header(results, "regression.csv")
    assert header.results == results
    assert header.filename == "regression.csv"


def test_footer_widget():
    """Test footer widget instantiation and inheritance."""
    footer = Footer()
    assert footer is not None
    assert isinstance(footer, TextualFooter)


def test_summary_metrics_classification():
    """Test summary metrics for classification."""
    results = EvaluationResults(
        mode=EvaluationMode.CLASSIFICATION,
        metrics={
            "accuracy": 0.92,
            "macro_avg_precision": 0.91,
            "macro_avg_recall": 0.90,
            "macro_avg_f1_score": 0.905,
            "cohen_kappa": 0.84,
        },
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=50,
    )

    widget = SummaryMetrics(results)
    assert widget.results == results


def test_summary_metrics_regression():
    """Test summary metrics for regression."""
    results = EvaluationResults(
        mode=EvaluationMode.REGRESSION,
        metrics={
            "r2_score": 0.996,
            "mae": 4900.0,
            "rmse": 4919.35,
            "mape": 0.0186,
        },
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=20,
    )

    widget = SummaryMetrics(results)
    assert widget.results == results


def test_metrics_table():
    """Test detailed metrics table with various metric types."""
    results = EvaluationResults(
        mode=EvaluationMode.CLASSIFICATION,
        metrics={
            "accuracy": 0.92,
            "macro_avg_precision": 0.91,
            "numpy_metric": np.float64(0.85),
            "int_metric": 42,
        },
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=50,
    )

    table = MetricsTable(results)
    assert table.results == results

    # Verify that the widget stores the correct results
    assert table.results.metrics["accuracy"] == 0.92
    assert table.results.metrics["macro_avg_precision"] == 0.91
    assert isinstance(table.results.metrics["numpy_metric"], np.number)
    assert table.results.metrics["int_metric"] == 42

    # Verify the compose method exists and is callable
    assert hasattr(table, 'compose')
    assert callable(table.compose)


def test_confusion_matrix_widget():
    """Test confusion matrix widget."""
    results = EvaluationResults(
        mode=EvaluationMode.CLASSIFICATION,
        metrics={
            "confusion_matrix": np.array([[8, 1], [1, 10]]),
            "labels": ["negative", "positive"],
        },
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=20,
    )

    widget = ConfusionMatrixWidget(results)
    assert widget.results == results

    # Verify the widget stores the correct confusion matrix and labels
    assert "confusion_matrix" in widget.results.metrics
    assert "labels" in widget.results.metrics
    assert widget.results.metrics["labels"] == ["negative", "positive"]

    # Verify the compose method exists and is callable
    assert hasattr(widget, 'compose')
    assert callable(widget.compose)


def test_confusion_matrix_widget_no_matrix():
    """Test confusion matrix widget when no matrix is available."""
    results = EvaluationResults(
        mode=EvaluationMode.CLASSIFICATION,
        metrics={"accuracy": 0.92},  # No confusion matrix
        predicted=np.array([]),
        gold=np.array([]),
        sample_count=20,
    )

    widget = ConfusionMatrixWidget(results)
    assert widget.results == results

    # Should still be composable without errors
    assert hasattr(widget, 'compose')
    assert callable(widget.compose)
