"""Tests for TUI widgets."""

from evalkit.tui.widgets.header import Header
from evalkit.types import EvaluationResults, EvaluationMode
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
