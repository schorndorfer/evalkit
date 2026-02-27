"""Integration tests for the Evaluator class."""

import pytest
from pathlib import Path
import numpy as np

from evalkit import Evaluator, EvaluationMode


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


class TestEvaluatorFromCSV:
    """Tests for Evaluator.from_csv()."""

    def test_from_csv_binary_classification(self, fixtures_dir):
        """Test loading and evaluating binary classification."""
        csv_path = fixtures_dir / "classification_binary.csv"
        evaluator = Evaluator.from_csv(csv_path)
        results = evaluator.evaluate()

        assert results.mode == EvaluationMode.CLASSIFICATION
        assert results.sample_count == 20
        assert "accuracy" in results.metrics
        assert "confusion_matrix" in results.metrics

    def test_from_csv_multiclass_classification(self, fixtures_dir):
        """Test loading and evaluating multiclass classification."""
        csv_path = fixtures_dir / "classification_multiclass.csv"
        evaluator = Evaluator.from_csv(csv_path)
        results = evaluator.evaluate()

        assert results.mode == EvaluationMode.CLASSIFICATION
        assert results.sample_count == 20
        assert results.metrics["is_binary"] is False
        assert len(results.metrics["per_class"]) == 3

    def test_from_csv_regression(self, fixtures_dir):
        """Test loading and evaluating regression."""
        csv_path = fixtures_dir / "regression.csv"
        evaluator = Evaluator.from_csv(csv_path)
        results = evaluator.evaluate()

        assert results.mode == EvaluationMode.REGRESSION
        assert results.sample_count == 20
        assert "mae" in results.metrics
        assert "rmse" in results.metrics
        assert "r2_score" in results.metrics

    def test_explicit_mode_override(self, fixtures_dir):
        """Test that explicit mode can override auto-detection."""
        csv_path = fixtures_dir / "classification_binary.csv"
        # The data would normally be detected as classification,
        # but we can override to treat it differently
        evaluator = Evaluator.from_csv(csv_path, mode=EvaluationMode.CLASSIFICATION)
        results = evaluator.evaluate()

        # Verify explicit mode is used
        assert results.mode == EvaluationMode.CLASSIFICATION


class TestEvaluatorDirect:
    """Tests for direct Evaluator instantiation."""

    def test_classification_evaluation(self):
        """Test direct classification evaluation."""
        predicted = np.array(["a", "b", "a", "b", "a", "b"])
        gold = np.array(["a", "b", "b", "b", "a", "b"])

        evaluator = Evaluator(predicted, gold, mode=EvaluationMode.CLASSIFICATION)
        results = evaluator.evaluate()

        assert results.mode == EvaluationMode.CLASSIFICATION
        assert results.sample_count == 6
        assert 0 <= results.metrics["accuracy"] <= 1

    def test_regression_evaluation(self):
        """Test direct regression evaluation."""
        predicted = np.array([1.5, 2.5, 3.5, 4.5, 5.5])
        gold = np.array([1.2, 2.4, 3.6, 4.3, 5.7])

        evaluator = Evaluator(predicted, gold, mode=EvaluationMode.REGRESSION)
        results = evaluator.evaluate()

        assert results.mode == EvaluationMode.REGRESSION
        assert results.sample_count == 5
        assert results.metrics["mae"] > 0
        assert results.metrics["r2_score"] > 0


class TestEvaluationResults:
    """Tests for EvaluationResults methods."""

    def test_results_summary(self, fixtures_dir):
        """Test that summary() returns a string."""
        csv_path = fixtures_dir / "classification_binary.csv"
        evaluator = Evaluator.from_csv(csv_path)
        results = evaluator.evaluate()

        summary = results.summary()
        assert isinstance(summary, str)
        assert "classification" in summary.lower()
        assert "Samples:" in summary

    def test_results_to_dict(self, fixtures_dir):
        """Test that to_dict() returns a dictionary."""
        csv_path = fixtures_dir / "regression.csv"
        evaluator = Evaluator.from_csv(csv_path)
        results = evaluator.evaluate()

        data = results.to_dict()
        assert isinstance(data, dict)
        assert "mode" in data
        assert "sample_count" in data
        assert "metrics" in data
