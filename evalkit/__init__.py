"""EvalKit: A comprehensive evaluation library for ML predictions."""

from evalkit.evaluator import Evaluator
from evalkit.types import EvaluationMode, EvaluationResults

__version__ = "0.1.0"

__all__ = [
    "Evaluator",
    "EvaluationMode",
    "EvaluationResults",
]
