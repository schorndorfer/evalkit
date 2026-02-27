"""Core evaluation logic."""

from pathlib import Path
from typing import Optional
import numpy as np

from evalkit.types import EvaluationMode, EvaluationResults
from evalkit.data import load_csv, detect_mode, validate_for_mode
from evalkit.metrics.classification import calculate_classification_metrics
from evalkit.metrics.regression import calculate_regression_metrics


class Evaluator:
    """Main evaluator class for ML predictions."""

    def __init__(
        self,
        predicted: np.ndarray,
        gold: np.ndarray,
        mode: Optional[EvaluationMode] = None,
        excluded_count: int = 0,
    ):
        """
        Initialize evaluator with data.

        Args:
            predicted: Predicted values
            gold: Ground truth values
            mode: Evaluation mode (auto-detect if None)
            excluded_count: Number of excluded samples
        """
        self.predicted = predicted
        self.gold = gold
        self.excluded_count = excluded_count
        self._mode = mode

    @classmethod
    def from_csv(
        cls,
        file_path: str | Path,
        pred_col: Optional[str] = None,
        gold_col: Optional[str] = None,
        mode: Optional[EvaluationMode] = None,
    ) -> "Evaluator":
        """
        Create evaluator from CSV file.

        Args:
            file_path: Path to CSV file
            pred_col: Column name for predictions
            gold_col: Column name for gold values
            mode: Explicit evaluation mode

        Returns:
            Evaluator instance
        """
        # Load and validate CSV
        pred_series, gold_series, excluded_count = load_csv(file_path, pred_col, gold_col)

        # Detect mode
        detected_mode = detect_mode(pred_series, gold_series, mode)

        # Validate and convert for mode
        pred_array, gold_array = validate_for_mode(pred_series, gold_series, detected_mode)

        return cls(pred_array, gold_array, detected_mode, excluded_count)

    def evaluate(
        self,
        mode: Optional[EvaluationMode] = None,
    ) -> EvaluationResults:
        """
        Run evaluation and return results.

        Args:
            mode: Override evaluation mode

        Returns:
            EvaluationResults object
        """
        # Use provided mode or fall back to instance mode
        eval_mode = mode or self._mode

        # If still no mode, auto-detect
        if eval_mode is None:
            import pandas as pd

            eval_mode = detect_mode(
                pd.Series(self.predicted),
                pd.Series(self.gold),
                None,
            )

        # Calculate metrics based on mode
        if eval_mode == EvaluationMode.CLASSIFICATION:
            metrics = calculate_classification_metrics(self.gold, self.predicted)
        else:
            metrics = calculate_regression_metrics(self.gold, self.predicted)

        return EvaluationResults(
            mode=eval_mode,
            metrics=metrics,
            predicted=self.predicted,
            gold=self.gold,
            sample_count=len(self.predicted),
            excluded_count=self.excluded_count,
        )
