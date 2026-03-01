"""Classification metrics calculation."""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    cohen_kappa_score,
    matthews_corrcoef,
)
from typing import Any


def calculate_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict[str, Any]:
    """
    Calculate comprehensive classification metrics.

    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels

    Returns:
        Dictionary of metric names and values
    """
    metrics = {}

    # Overall accuracy
    metrics["accuracy"] = accuracy_score(y_true, y_pred)

    # Precision, Recall, F1-Score with different averaging strategies
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    metrics["macro_avg_precision"] = precision
    metrics["macro_avg_recall"] = recall
    metrics["macro_avg_f1_score"] = f1

    # Weighted averages (accounts for class imbalance)
    precision_w, recall_w, f1_w, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )
    metrics["weighted_avg_precision"] = precision_w
    metrics["weighted_avg_recall"] = recall_w
    metrics["weighted_avg_f1_score"] = f1_w

    # Micro averages
    precision_mi, recall_mi, f1_mi, _ = precision_recall_fscore_support(
        y_true, y_pred, average="micro", zero_division=0
    )
    metrics["micro_avg_precision"] = precision_mi
    metrics["micro_avg_recall"] = recall_mi
    metrics["micro_avg_f1_score"] = f1_mi

    # Cohen's Kappa (agreement accounting for chance)
    metrics["cohen_kappa"] = cohen_kappa_score(y_true, y_pred)

    # Matthews Correlation Coefficient (good for imbalanced datasets)
    metrics["matthews_corrcoef"] = matthews_corrcoef(y_true, y_pred)

    # Confusion matrix
    conf_matrix = confusion_matrix(y_true, y_pred)
    metrics["confusion_matrix"] = conf_matrix

    # Get unique labels for per-class metrics
    labels = sorted(set(y_true) | set(y_pred))
    metrics["labels"] = labels

    # Per-class metrics
    precision_per_class, recall_per_class, f1_per_class, support_per_class = (
        precision_recall_fscore_support(y_true, y_pred, average=None, zero_division=0)
    )

    per_class_metrics = {}
    for idx, label in enumerate(labels):
        per_class_metrics[str(label)] = {
            "precision": precision_per_class[idx],
            "recall": recall_per_class[idx],
            "f1_score": f1_per_class[idx],
            "support": int(support_per_class[idx]),
        }
    metrics["per_class"] = per_class_metrics

    # Check if binary classification
    if len(labels) == 2:
        metrics["is_binary"] = True
        # For binary classification, calculate specificity and sensitivity
        tn, fp, fn, tp = conf_matrix.ravel()
        metrics["specificity"] = tn / (tn + fp) if (tn + fp) > 0 else 0
        metrics["sensitivity"] = tp / (tp + fn) if (tp + fn) > 0 else 0
        metrics["true_negatives"] = int(tn)
        metrics["false_positives"] = int(fp)
        metrics["false_negatives"] = int(fn)
        metrics["true_positives"] = int(tp)

        # Store row indices for each quadrant to enable sample inspection
        neg_label, pos_label = labels[0], labels[1]
        metrics["tp_indices"] = list(np.where((y_true == pos_label) & (y_pred == pos_label))[0])
        metrics["tn_indices"] = list(np.where((y_true == neg_label) & (y_pred == neg_label))[0])
        metrics["fp_indices"] = list(np.where((y_true == neg_label) & (y_pred == pos_label))[0])
        metrics["fn_indices"] = list(np.where((y_true == pos_label) & (y_pred == neg_label))[0])
    else:
        metrics["is_binary"] = False

    return metrics
