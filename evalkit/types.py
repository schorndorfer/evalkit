"""Type definitions and enums for evalkit."""

from enum import Enum
from dataclasses import dataclass
from typing import Any
import numpy as np


class EvaluationMode(Enum):
    """Evaluation mode for predictions."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"


@dataclass
class EvaluationResults:
    """Container for evaluation results."""

    mode: EvaluationMode
    metrics: dict[str, Any]
    predicted: np.ndarray
    gold: np.ndarray
    sample_count: int
    excluded_count: int = 0

    def summary(self) -> str:
        """Return a text summary of the results."""
        lines = [
            f"Evaluation Mode: {self.mode.value}",
            f"Samples: {self.sample_count}",
        ]
        if self.excluded_count > 0:
            lines.append(f"Excluded (missing values): {self.excluded_count}")
        lines.append("\nMetrics:")
        for key, value in self.metrics.items():
            if isinstance(value, (int, float, np.number)):
                lines.append(f"  {key}: {value:.2f}")
            else:
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert results to dictionary format."""
        return {
            "mode": self.mode.value,
            "sample_count": self.sample_count,
            "excluded_count": self.excluded_count,
            "metrics": self.metrics,
        }
