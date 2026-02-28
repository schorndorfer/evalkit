"""Tests for output formatters."""

import pytest
from pathlib import Path
import json
import tempfile
from io import StringIO

from evalkit import Evaluator
from evalkit.formatters.exporters import (
    export_to_json,
    export_to_csv,
    export_to_markdown,
    export_results,
)
from evalkit.formatters.visualizers import generate_visualizations
from evalkit.formatters.rich_console import display_results
from rich.console import Console


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def classification_results(fixtures_dir):
    """Get classification results for testing."""
    csv_path = fixtures_dir / "classification_binary.csv"
    evaluator = Evaluator.from_csv(csv_path)
    return evaluator.evaluate()


@pytest.fixture
def regression_results(fixtures_dir):
    """Get regression results for testing."""
    csv_path = fixtures_dir / "regression.csv"
    evaluator = Evaluator.from_csv(csv_path)
    return evaluator.evaluate()


class TestExporters:
    """Tests for result exporters."""

    def test_export_to_json(self, classification_results):
        """Test JSON export."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = Path(f.name)

        try:
            export_to_json(classification_results, output_path)
            assert output_path.exists()

            with open(output_path) as f:
                data = json.load(f)

            assert "mode" in data
            assert "metrics" in data
            assert data["sample_count"] == 20
        finally:
            output_path.unlink()

    def test_export_to_csv(self, regression_results):
        """Test CSV export."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            output_path = Path(f.name)

        try:
            export_to_csv(regression_results, output_path)
            assert output_path.exists()

            with open(output_path) as f:
                content = f.read()

            assert "Metric,Value" in content
            assert "regression" in content
        finally:
            output_path.unlink()

    def test_export_to_markdown(self, classification_results):
        """Test Markdown export."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = Path(f.name)

        try:
            export_to_markdown(classification_results, output_path)
            assert output_path.exists()

            with open(output_path) as f:
                content = f.read()

            assert "# Evaluation Results" in content
            assert "Classification" in content
            assert "| Metric | Value |" in content
        finally:
            output_path.unlink()

    def test_export_results_dispatcher(self, classification_results):
        """Test export_results dispatches to correct format handler."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test JSON
            json_path = Path(tmpdir) / "results.json"
            export_results(classification_results, json_path)
            assert json_path.exists()

            # Test CSV
            csv_path = Path(tmpdir) / "results.csv"
            export_results(classification_results, csv_path)
            assert csv_path.exists()

            # Test Markdown
            md_path = Path(tmpdir) / "results.md"
            export_results(classification_results, md_path)
            assert md_path.exists()

    def test_export_unsupported_format(self, classification_results):
        """Test export_results raises error for unsupported format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            invalid_path = Path(tmpdir) / "results.txt"

            with pytest.raises(ValueError, match="Unsupported file extension"):
                export_results(classification_results, invalid_path)


class TestVisualizers:
    """Tests for visualization generation."""

    def test_generate_classification_visualizations(self, classification_results):
        """Test classification visualization generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            saved_files = generate_visualizations(classification_results, output_dir)

            assert len(saved_files) > 0
            assert all(f.exists() for f in saved_files)
            assert any("confusion_matrix" in f.name for f in saved_files)

    def test_generate_regression_visualizations(self, regression_results):
        """Test regression visualization generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            saved_files = generate_visualizations(regression_results, output_dir)

            assert len(saved_files) > 0
            assert all(f.exists() for f in saved_files)
            assert any("predicted_vs_actual" in f.name for f in saved_files)
            assert any("residual" in f.name for f in saved_files)


class TestRichConsole:
    """Tests for rich console output."""

    def test_display_classification_results(self, classification_results):
        """Test displaying classification results."""
        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True, width=120)

        # Should not raise any exceptions
        display_results(classification_results, console)

        output = string_io.getvalue()

        # Verify key content is present
        assert "Evaluation Results" in output
        assert "Classification" in output
        assert "Accuracy" in output
        assert "Samples:" in output

    def test_display_regression_results(self, regression_results):
        """Test displaying regression results."""
        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True, width=120)

        # Should not raise any exceptions
        display_results(regression_results, console)

        output = string_io.getvalue()

        # Verify key content is present
        assert "Evaluation Results" in output
        assert "Regression" in output
        assert "R² Score" in output
        assert "MAE" in output
        assert "RMSE" in output

    def test_display_binary_classification_specifics(self, classification_results):
        """Test binary classification displays sensitivity, specificity and confusion counts."""
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True, width=120)

        display_results(classification_results, console)
        output = string_io.getvalue()

        # Binary classification should show these metrics
        assert "Sensitivity" in output
        assert "Specificity" in output
        assert "True Positives" in output
        assert "False Positives" in output

    def test_display_with_no_console(self, classification_results):
        """Test display_results creates console when none provided."""
        # Should not raise - creates its own console
        display_results(classification_results, None)

    def test_display_confusion_matrix(self, classification_results):
        """Test confusion matrix is displayed."""
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True, width=120)

        display_results(classification_results, console)
        output = string_io.getvalue()

        assert "Confusion Matrix" in output

    def test_display_per_class_metrics(self, classification_results):
        """Test per-class metrics are displayed."""
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True, width=120)

        display_results(classification_results, console)
        output = string_io.getvalue()

        assert "Per-Class Metrics" in output
        assert "Precision" in output
        assert "Recall" in output
        assert "F1-Score" in output
