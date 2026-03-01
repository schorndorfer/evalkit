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
        assert metrics["sensitivity"] == 1.0
        assert metrics["specificity"] == 1.0

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

    def test_binary_sensitivity_specificity(self):
        """Test sensitivity and specificity calculation for binary classification."""
        # TP=2, TN=3, FP=1, FN=2
        y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0])
        y_pred = np.array([1, 1, 0, 0, 0, 0, 0, 1])

        metrics = calculate_classification_metrics(y_true, y_pred)

        # Sensitivity = TP / (TP + FN) = 2 / (2 + 2) = 0.5
        assert metrics["sensitivity"] == 0.5
        # Specificity = TN / (TN + FP) = 3 / (3 + 1) = 0.75
        assert metrics["specificity"] == 0.75
        assert metrics["true_positives"] == 2
        assert metrics["true_negatives"] == 3
        assert metrics["false_positives"] == 1
        assert metrics["false_negatives"] == 2

    def test_binary_quadrant_indices_stored(self):
        """Test that TP/TN/FP/FN row indices are stored for binary classification."""
        # labels sorted: [0, 1] -> neg=0, pos=1
        # Indices: 0→TN, 1→TP, 2→FP, 3→FN, 4→TN, 5→TP
        y_true = np.array([0, 1, 0, 1, 0, 1])
        y_pred = np.array([0, 1, 1, 0, 0, 1])

        metrics = calculate_classification_metrics(y_true, y_pred)

        assert "tp_indices" in metrics
        assert "tn_indices" in metrics
        assert "fp_indices" in metrics
        assert "fn_indices" in metrics

        assert sorted(metrics["tp_indices"]) == [1, 5]
        assert sorted(metrics["tn_indices"]) == [0, 4]
        assert sorted(metrics["fp_indices"]) == [2]
        assert sorted(metrics["fn_indices"]) == [3]

        # Counts should match TP/TN/FP/FN metric values
        assert len(metrics["tp_indices"]) == metrics["true_positives"]
        assert len(metrics["tn_indices"]) == metrics["true_negatives"]
        assert len(metrics["fp_indices"]) == metrics["false_positives"]
        assert len(metrics["fn_indices"]) == metrics["false_negatives"]

    def test_multiclass_no_quadrant_indices(self):
        """Test that quadrant indices are not stored for multiclass classification."""
        y_true = np.array(["cat", "dog", "bird", "cat"])
        y_pred = np.array(["cat", "dog", "cat", "cat"])

        metrics = calculate_classification_metrics(y_true, y_pred)

        assert "tp_indices" not in metrics
        assert "tn_indices" not in metrics
        assert "fp_indices" not in metrics
        assert "fn_indices" not in metrics

    def test_binary_quadrant_indices_empty_category(self):
        """Test quadrant indices when a category has zero samples (perfect predictions)."""
        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 1])

        metrics = calculate_classification_metrics(y_true, y_pred)

        assert metrics["fp_indices"] == []
        assert metrics["fn_indices"] == []
        assert len(metrics["tp_indices"]) == 2
        assert len(metrics["tn_indices"]) == 2


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
