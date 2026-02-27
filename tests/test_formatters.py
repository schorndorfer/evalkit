"""Tests for output formatters."""

import pytest
from pathlib import Path
import json
import tempfile

from evalkit import Evaluator
from evalkit.formatters.exporters import export_to_json, export_to_csv, export_to_markdown
from evalkit.formatters.visualizers import generate_visualizations


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
