"""Command-line interface for EvalKit."""

import sys
import click
from rich.console import Console

from evalkit import Evaluator, EvaluationMode
from evalkit.data import DataValidationError
from evalkit.formatters.rich_console import display_results
from evalkit.formatters.exporters import export_results
from evalkit.formatters.visualizers import generate_visualizations

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """EvalKit: Comprehensive evaluation CLI for ML predictions."""
    pass


@cli.command()
@click.argument("csv_file", type=click.Path(exists=True))
@click.option(
    "--pred",
    "-p",
    "pred_col",
    type=str,
    default=None,
    help="Column name for predictions (auto-detect if not specified)",
)
@click.option(
    "--gold",
    "-g",
    "gold_col",
    type=str,
    default=None,
    help="Column name for gold/actual values (auto-detect if not specified)",
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["classification", "regression"], case_sensitive=False),
    default=None,
    help="Evaluation mode (auto-detect if not specified)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Save results to file (format based on extension: .json, .csv, .md)",
)
@click.option(
    "--visualize",
    "-v",
    is_flag=True,
    help="Generate and save visualization plots",
)
@click.option(
    "--viz-dir",
    type=click.Path(),
    default="./eval_plots",
    help="Directory for visualization outputs (default: ./eval_plots)",
)
@click.option(
    "--no-display",
    is_flag=True,
    help="Skip terminal output (useful with --output)",
)
def evaluate(csv_file, pred_col, gold_col, mode, output, visualize, viz_dir, no_display):
    """
    Evaluate predictions from a CSV file.

    CSV_FILE: Path to CSV file containing predictions and gold values.
    """
    try:
        # Convert mode string to enum if provided
        eval_mode = None
        if mode:
            eval_mode = (
                EvaluationMode.CLASSIFICATION
                if mode.lower() == "classification"
                else EvaluationMode.REGRESSION
            )

        # Load data and create evaluator
        evaluator = Evaluator.from_csv(csv_file, pred_col, gold_col, eval_mode)

        # Run evaluation
        results = evaluator.evaluate()

        # Display results in terminal (unless --no-display)
        if not no_display:
            display_results(results, console)

        # Export to file if requested
        if output:
            try:
                export_results(results, output)
                console.print(f"[green]✓ Results saved to {output}[/green]")
            except Exception as e:
                console.print(f"[red]Error exporting results: {e}[/red]", file=sys.stderr)
                sys.exit(2)

        # Generate visualizations if requested
        if visualize:
            try:
                saved_files = generate_visualizations(results, viz_dir)
                console.print(
                    f"[green]✓ Generated {len(saved_files)} visualization(s) in {viz_dir}[/green]"
                )
                for file_path in saved_files:
                    console.print(f"  - {file_path.name}")
            except Exception as e:
                console.print(f"[yellow]⚠ Warning: Visualization failed: {e}[/yellow]")

        sys.exit(0)

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]", file=sys.stderr)
        sys.exit(1)
    except DataValidationError as e:
        console.print(f"[red]Error: {e}[/red]", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(2)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
