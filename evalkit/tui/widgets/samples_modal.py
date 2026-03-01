"""Samples modal widget for viewing confusion matrix quadrant examples."""

import numpy as np
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static


MAX_SAMPLES = 50


class SamplesModal(ModalScreen):
    """
    Modal screen displaying sample predictions for a confusion matrix quadrant.

    Shows a scrollable table of examples (row index, true label, predicted label)
    from a selected TP/TN/FP/FN category.
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
        ("q", "app.pop_screen", "Close"),
    ]

    DEFAULT_CSS = """
    SamplesModal {
        align: center middle;
    }

    SamplesModal > Vertical {
        background: $surface;
        border: thick $primary;
        width: 70;
        height: 30;
        padding: 1 2;
    }

    SamplesModal #modal-title {
        text-align: center;
        margin-bottom: 1;
    }

    SamplesModal #no-samples {
        text-align: center;
        color: $text-muted;
        margin: 2;
    }

    SamplesModal DataTable {
        height: 1fr;
        margin-bottom: 1;
    }

    SamplesModal Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        category: str,
        indices: list[int],
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> None:
        """
        Initialize samples modal.

        Args:
            category: Name of the confusion matrix category (e.g. "True Positives")
            indices: Row indices of samples in this category
            y_true: Ground truth labels array
            y_pred: Predicted labels array
        """
        super().__init__()
        self.category = category
        self.all_indices = indices
        self.display_indices = indices[:MAX_SAMPLES]
        self.y_true = y_true
        self.y_pred = y_pred

    def compose(self) -> ComposeResult:
        """
        Compose samples modal content.

        Returns:
            Generator yielding modal widgets
        """
        total = len(self.all_indices)
        showing = len(self.display_indices)

        title = f"[cyan bold]{self.category}[/cyan bold]"
        if total == 0:
            subtitle = "[dim]0 samples[/dim]"
        elif total > MAX_SAMPLES:
            subtitle = f"[dim]Showing first {showing} of {total} samples[/dim]"
        else:
            subtitle = f"[dim]{total} sample{'s' if total != 1 else ''}[/dim]"

        with Vertical():
            yield Static(f"{title}\n{subtitle}", id="modal-title")

            if not self.display_indices:
                yield Static(
                    "[dim]No samples found in this category.[/dim]",
                    id="no-samples",
                )
            else:
                yield DataTable(id="samples-table")

            yield Button("Close [dim](Esc / q)[/dim]", variant="primary", id="close-btn")

    def on_mount(self) -> None:
        """Populate the data table after mounting."""
        if not self.display_indices:
            return

        table = self.query_one("#samples-table", DataTable)
        table.add_columns("Row", "True Label", "Predicted Label")
        for idx in self.display_indices:
            table.add_row(str(idx), str(self.y_true[idx]), str(self.y_pred[idx]))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button press events.

        Args:
            event: Button pressed event
        """
        if event.button.id == "close-btn":
            self.dismiss()
