"""Data loading and validation utilities."""

from pathlib import Path
from typing import Optional
import pandas as pd
import numpy as np
from rich.console import Console

from evalkit.types import EvaluationMode

console = Console()


class DataValidationError(Exception):
    """Raised when data validation fails."""

    pass


def load_csv(
    file_path: str | Path,
    pred_col: Optional[str] = None,
    gold_col: Optional[str] = None,
) -> tuple[pd.Series, pd.Series, int]:
    """
    Load and validate CSV file containing predictions and gold values.

    Args:
        file_path: Path to CSV file
        pred_col: Column name for predictions (auto-detect if None)
        gold_col: Column name for gold/actual values (auto-detect if None)

    Returns:
        Tuple of (predicted, gold, excluded_count)

    Raises:
        DataValidationError: If validation fails
        FileNotFoundError: If file doesn't exist
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Could not find '{file_path}'. Please check the file path.")

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise DataValidationError(
            f"CSV parsing failed: {e}. Ensure the file is properly formatted."
        )

    if df.empty:
        raise DataValidationError("CSV file is empty.")

    # Auto-detect columns if not specified
    if pred_col is None and gold_col is None:
        if len(df.columns) == 2:
            pred_col, gold_col = df.columns[0], df.columns[1]
            console.print(
                f"[dim]Using columns: '{pred_col}' (predicted) and '{gold_col}' (gold)[/dim]"
            )
        else:
            available = ", ".join(f"'{col}'" for col in df.columns)
            raise DataValidationError(
                f"Could not auto-detect columns. CSV has {len(df.columns)} columns. "
                f"Please specify --pred and --gold. Available columns: {available}"
            )
    elif pred_col is None or gold_col is None:
        raise DataValidationError("Both --pred and --gold must be specified together.")

    # Validate columns exist
    if pred_col not in df.columns:
        available = ", ".join(f"'{col}'" for col in df.columns)
        raise DataValidationError(f"Column '{pred_col}' not found. Available columns: {available}")
    if gold_col not in df.columns:
        available = ", ".join(f"'{col}'" for col in df.columns)
        raise DataValidationError(f"Column '{gold_col}' not found. Available columns: {available}")

    predicted = df[pred_col]
    gold = df[gold_col]

    # Check for missing values
    missing_mask = predicted.isna() | gold.isna()
    excluded_count = missing_mask.sum()

    if excluded_count > 0:
        console.print(
            f"[yellow]⚠ Found {excluded_count} rows with missing values (will be excluded)[/yellow]"
        )
        predicted = predicted[~missing_mask]
        gold = gold[~missing_mask]

    final_count = len(predicted)
    if final_count == 0:
        raise DataValidationError(
            "No valid samples found after filtering missing values. Check your data."
        )

    console.print(f"[green]✓ Loaded {final_count} samples from {file_path.name}[/green]")

    return predicted, gold, excluded_count


def detect_mode(
    predicted: pd.Series,
    gold: pd.Series,
    explicit_mode: Optional[EvaluationMode] = None,
) -> EvaluationMode:
    """
    Detect evaluation mode (classification or regression).

    Args:
        predicted: Predicted values
        gold: Gold/actual values
        explicit_mode: If provided, use this mode explicitly

    Returns:
        Detected or explicit evaluation mode
    """
    if explicit_mode is not None:
        console.print(f"[dim]Using explicit mode: {explicit_mode.value}[/dim]")
        return explicit_mode

    # Try to detect based on data types
    try:
        # Try converting to float
        pred_numeric = pd.to_numeric(predicted, errors="raise")
        gold_numeric = pd.to_numeric(gold, errors="raise")

        # Check if values are continuous or discrete
        pred_unique = len(pred_numeric.unique())
        gold_unique = len(gold_numeric.unique())
        total_unique = max(pred_unique, gold_unique)

        # Check if values have decimal points (continuous)
        has_decimals = (
            (pred_numeric % 1 != 0).any() or (gold_numeric % 1 != 0).any()
        )

        # Heuristic for mode detection:
        # - If values have decimals and high uniqueness, it's regression
        # - If few unique values (<=10) and no decimals, it's classification
        # - Otherwise use ratio: <30% unique = classification, else regression
        unique_ratio = total_unique / len(predicted)

        if has_decimals and unique_ratio > 0.5:
            # Continuous decimal values with high uniqueness -> regression
            mode = EvaluationMode.REGRESSION
            console.print("[cyan]ℹ Auto-detected mode: regression (continuous values)[/cyan]")
        elif total_unique <= 10 and not has_decimals:
            # Few discrete integer values -> classification
            mode = EvaluationMode.CLASSIFICATION
            console.print(
                f"[cyan]ℹ Auto-detected mode: classification ({total_unique} unique values)[/cyan]"
            )
        elif unique_ratio < 0.3:
            # Low uniqueness ratio -> classification
            mode = EvaluationMode.CLASSIFICATION
            console.print(
                f"[cyan]ℹ Auto-detected mode: classification ({total_unique} unique values)[/cyan]"
            )
        else:
            # Default to regression for ambiguous cases
            mode = EvaluationMode.REGRESSION
            console.print("[cyan]ℹ Auto-detected mode: regression (continuous values)[/cyan]")

        return mode

    except (ValueError, TypeError):
        # Non-numeric values, definitely classification
        mode = EvaluationMode.CLASSIFICATION
        unique_count = len(set(predicted) | set(gold))
        console.print(
            f"[cyan]ℹ Auto-detected mode: classification ({unique_count} unique classes)[/cyan]"
        )
        return mode


def validate_for_mode(
    predicted: pd.Series,
    gold: pd.Series,
    mode: EvaluationMode,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Validate and convert data for the specified evaluation mode.

    Args:
        predicted: Predicted values
        gold: Gold/actual values
        mode: Evaluation mode

    Returns:
        Tuple of (predicted_array, gold_array) as numpy arrays

    Raises:
        DataValidationError: If data is incompatible with mode
    """
    if mode == EvaluationMode.REGRESSION:
        try:
            pred_array = pd.to_numeric(predicted, errors="raise").to_numpy()
            gold_array = pd.to_numeric(gold, errors="raise").to_numpy()
        except (ValueError, TypeError) as e:
            raise DataValidationError(
                f"Cannot perform regression on non-numeric data: {e}. "
                "Use --mode classification for categorical data."
            )
    else:
        # Classification - keep as-is (can be strings or numbers)
        pred_array = predicted.to_numpy()
        gold_array = gold.to_numpy()

    return pred_array, gold_array
