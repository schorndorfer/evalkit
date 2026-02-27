"""Tests for data loading and validation."""

import pytest
from pathlib import Path
import pandas as pd

from evalkit.data import load_csv, detect_mode, validate_for_mode, DataValidationError
from evalkit.types import EvaluationMode


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


class TestLoadCSV:
    """Tests for CSV loading."""

    def test_load_binary_classification(self, fixtures_dir):
        """Test loading binary classification CSV."""
        csv_path = fixtures_dir / "classification_binary.csv"
        pred, gold, excluded = load_csv(csv_path)

        assert len(pred) == 20
        assert len(gold) == 20
        assert excluded == 0

    def test_load_regression(self, fixtures_dir):
        """Test loading regression CSV."""
        csv_path = fixtures_dir / "regression.csv"
        pred, gold, excluded = load_csv(csv_path)

        assert len(pred) == 20
        assert len(gold) == 20
        assert excluded == 0

    def test_load_with_explicit_columns(self, fixtures_dir):
        """Test loading with explicit column names."""
        csv_path = fixtures_dir / "classification_multiclass.csv"
        pred, gold, excluded = load_csv(csv_path, pred_col="predicted", gold_col="actual")

        assert len(pred) == 20
        assert len(gold) == 20

    def test_file_not_found(self):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_csv("nonexistent.csv")

    def test_invalid_column_name(self, fixtures_dir):
        """Test error with invalid column name."""
        csv_path = fixtures_dir / "classification_binary.csv"
        with pytest.raises(DataValidationError, match="Column.*not found"):
            load_csv(csv_path, pred_col="invalid", gold_col="gold")


class TestDetectMode:
    """Tests for mode detection."""

    def test_detect_classification_strings(self):
        """Test detection of classification with string values."""
        pred = pd.Series(["cat", "dog", "cat", "bird"])
        gold = pd.Series(["cat", "dog", "bird", "bird"])

        mode = detect_mode(pred, gold)
        assert mode == EvaluationMode.CLASSIFICATION

    def test_detect_classification_few_values(self):
        """Test detection of classification with few unique numeric values."""
        pred = pd.Series([0, 1, 0, 1, 0, 1])
        gold = pd.Series([0, 1, 1, 1, 0, 1])

        mode = detect_mode(pred, gold)
        assert mode == EvaluationMode.CLASSIFICATION

    def test_detect_regression(self):
        """Test detection of regression with continuous values."""
        pred = pd.Series([1.5, 2.7, 3.2, 4.8, 5.1, 6.3, 7.9])
        gold = pd.Series([1.2, 2.5, 3.4, 4.6, 5.3, 6.1, 8.0])

        mode = detect_mode(pred, gold)
        assert mode == EvaluationMode.REGRESSION

    def test_explicit_mode_override(self):
        """Test that explicit mode overrides detection."""
        pred = pd.Series([1, 2, 3, 4, 5])
        gold = pd.Series([1, 2, 3, 4, 5])

        mode = detect_mode(pred, gold, EvaluationMode.REGRESSION)
        assert mode == EvaluationMode.REGRESSION


class TestValidateForMode:
    """Tests for mode validation."""

    def test_validate_regression_numeric(self):
        """Test validation of numeric data for regression."""
        pred = pd.Series([1.0, 2.0, 3.0])
        gold = pd.Series([1.1, 2.1, 3.1])

        pred_array, gold_array = validate_for_mode(pred, gold, EvaluationMode.REGRESSION)

        assert len(pred_array) == 3
        assert len(gold_array) == 3

    def test_validate_regression_rejects_strings(self):
        """Test that regression rejects non-numeric data."""
        pred = pd.Series(["a", "b", "c"])
        gold = pd.Series(["a", "b", "c"])

        with pytest.raises(DataValidationError, match="Cannot perform regression"):
            validate_for_mode(pred, gold, EvaluationMode.REGRESSION)

    def test_validate_classification_accepts_strings(self):
        """Test that classification accepts string data."""
        pred = pd.Series(["cat", "dog", "bird"])
        gold = pd.Series(["cat", "dog", "bird"])

        pred_array, gold_array = validate_for_mode(pred, gold, EvaluationMode.CLASSIFICATION)

        assert len(pred_array) == 3
        assert len(gold_array) == 3
