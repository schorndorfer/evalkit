"""Regression metrics calculation."""

import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    explained_variance_score,
    median_absolute_error,
    max_error,
    mean_absolute_percentage_error,
)
from typing import Any


def calculate_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict[str, Any]:
    """
    Calculate comprehensive regression metrics.

    Args:
        y_true: Ground truth values
        y_pred: Predicted values

    Returns:
        Dictionary of metric names and values
    """
    metrics = {}

    # Mean Absolute Error
    metrics["mae"] = mean_absolute_error(y_true, y_pred)

    # Mean Squared Error
    metrics["mse"] = mean_squared_error(y_true, y_pred)

    # Root Mean Squared Error
    metrics["rmse"] = np.sqrt(metrics["mse"])

    # R² Score (coefficient of determination)
    metrics["r2_score"] = r2_score(y_true, y_pred)

    # Adjusted R² (adjusted for number of predictors)
    # For simple evaluation, we assume 1 predictor
    n = len(y_true)
    p = 1  # number of predictors
    if n > p + 1:
        adj_r2 = 1 - (1 - metrics["r2_score"]) * (n - 1) / (n - p - 1)
        metrics["adjusted_r2"] = adj_r2
    else:
        metrics["adjusted_r2"] = metrics["r2_score"]

    # Mean Absolute Percentage Error
    # Only calculate if no zeros in y_true (to avoid division by zero)
    if not np.any(y_true == 0):
        try:
            metrics["mape"] = mean_absolute_percentage_error(y_true, y_pred)
        except Exception:
            metrics["mape"] = None
    else:
        metrics["mape"] = None

    # Median Absolute Error (robust to outliers)
    metrics["median_absolute_error"] = median_absolute_error(y_true, y_pred)

    # Max Error (worst-case prediction)
    metrics["max_error"] = max_error(y_true, y_pred)

    # Explained Variance Score
    metrics["explained_variance"] = explained_variance_score(y_true, y_pred)

    # Additional useful statistics
    residuals = y_true - y_pred
    metrics["mean_residual"] = float(np.mean(residuals))
    metrics["std_residual"] = float(np.std(residuals))

    # Store residuals for visualization
    metrics["residuals"] = residuals

    return metrics
