"""Tests for metrics calculation."""

import numpy as np

from evalkit.metrics.classification import calculate_classification_metrics
from evalkit.metrics.regression import calculate_regression_metrics


class TestClassificationMetrics:
    """Tests for classification metrics."""

    def test_perfect_binary_classification(self):
        """Test metrics with perfect predictions."""
        y_true = np.array([0, 1, 0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 1, 0, 1])

        metrics = calculate_classification_metrics(y_true, y_pred)

        assert metrics["accuracy"] == 1.0
        assert metrics["macro_avg_precision"] == 1.0
        assert metrics["macro_avg_recall"] == 1.0
        assert metrics["macro_avg_f1_score"] == 1.0
        assert metrics["is_binary"] is True

    def test_binary_classification_with_errors(self):
        """Test metrics with some errors."""
        y_true = np.array([0, 1, 0, 1, 0, 1, 0, 1])
        y_pred = np.array([0, 1, 1, 1, 0, 0, 0, 1])  # 2 errors

        metrics = calculate_classification_metrics(y_true, y_pred)

        assert metrics["accuracy"] == 0.75
        assert 0 < metrics["macro_avg_f1_score"] < 1

    def test_multiclass_classification(self):
        """Test multiclass classification metrics."""
        y_true = np.array(["cat", "dog", "bird", "cat", "dog", "bird"])
        y_pred = np.array(["cat", "dog", "bird", "cat", "dog", "bird"])

        metrics = calculate_classification_metrics(y_true, y_pred)

        assert metrics["accuracy"] == 1.0
        assert metrics["is_binary"] is False
        assert len(metrics["per_class"]) == 3

    def test_confusion_matrix_present(self):
        """Test that confusion matrix is calculated."""
        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 1, 1])

        metrics = calculate_classification_metrics(y_true, y_pred)

        assert "confusion_matrix" in metrics
        assert metrics["confusion_matrix"].shape == (2, 2)


class TestRegressionMetrics:
    """Tests for regression metrics."""

    def test_perfect_regression(self):
        """Test metrics with perfect predictions."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        metrics = calculate_regression_metrics(y_true, y_pred)

        assert metrics["mae"] == 0.0
        assert metrics["mse"] == 0.0
        assert metrics["rmse"] == 0.0
        assert metrics["r2_score"] == 1.0

    def test_regression_with_errors(self):
        """Test metrics with prediction errors."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.1, 2.1, 2.9, 4.1, 4.9])

        metrics = calculate_regression_metrics(y_true, y_pred)

        assert 0 < metrics["mae"] < 0.2
        assert 0 < metrics["rmse"] < 0.2
        assert 0.9 < metrics["r2_score"] <= 1.0

    def test_residuals_calculated(self):
        """Test that residuals are calculated."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.1, 2.1, 2.9, 4.1, 4.9])

        metrics = calculate_regression_metrics(y_true, y_pred)

        assert "residuals" in metrics
        assert len(metrics["residuals"]) == len(y_true)

    def test_mape_with_zeros(self):
        """Test MAPE is None when y_true contains zeros."""
        y_true = np.array([0.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        metrics = calculate_regression_metrics(y_true, y_pred)

        assert metrics["mape"] is None
