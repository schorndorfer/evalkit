"""Integration tests for TUI."""

import pytest
from evalkit.tui import EvalKitApp
from evalkit import Evaluator, EvaluationMode
from pathlib import Path


@pytest.fixture
def classification_app() -> EvalKitApp:
    """Create TUI app with classification data."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    csv_path = fixtures_dir / "classification_binary.csv"

    evaluator = Evaluator.from_csv(csv_path)
    results = evaluator.evaluate()

    return EvalKitApp(results, "test.csv")


@pytest.fixture
def regression_app() -> EvalKitApp:
    """Create TUI app with regression data."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    csv_path = fixtures_dir / "regression.csv"

    evaluator = Evaluator.from_csv(csv_path)
    results = evaluator.evaluate()

    return EvalKitApp(results, "test.csv")


def test_app_initializes_classification(classification_app):
    """Test TUI app initializes with classification data."""
    assert classification_app.results.mode == EvaluationMode.CLASSIFICATION
    assert classification_app.filename == "test.csv"


def test_app_initializes_regression(regression_app):
    """Test TUI app initializes with regression data."""
    assert regression_app.results.mode == EvaluationMode.REGRESSION
    assert regression_app.filename == "test.csv"


@pytest.mark.asyncio
async def test_app_composes_widgets(classification_app):
    """Test app composes all required widgets."""
    async with classification_app.run_test() as pilot:
        # Check header exists
        assert classification_app.query_one("Header")

        # Check footer exists
        assert classification_app.query_one("Footer")

        # Check dashboard layout
        assert classification_app.query_one("DashboardLayout")
