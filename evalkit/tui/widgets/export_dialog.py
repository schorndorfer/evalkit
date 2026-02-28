"""Export dialog widget for TUI."""

from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, RadioButton, RadioSet


class ExportDialog(ModalScreen[dict[str, str] | None]):
    """
    Modal dialog for exporting evaluation results.

    Allows users to select export format (JSON, CSV, Markdown) and
    specify output path. Returns a dictionary with 'format' and 'path'
    keys on successful export, or None if cancelled.
    """

    DEFAULT_CSS = """
    ExportDialog {
        align: center middle;
    }

    ExportDialog > Grid {
        background: $surface;
        border: thick $primary;
        width: 60;
        height: 20;
        padding: 1 2;
        grid-size: 2 4;
        grid-rows: auto auto auto auto;
    }

    ExportDialog Label {
        width: 100%;
        content-align: left middle;
    }

    ExportDialog RadioSet {
        width: 100%;
    }

    ExportDialog Input {
        width: 100%;
    }

    ExportDialog Button {
        width: 100%;
    }
    """

    def __init__(self) -> None:
        """Initialize export dialog."""
        super().__init__()
        self.selected_format = "json"

    def compose(self) -> ComposeResult:
        """
        Compose export dialog content.

        Returns:
            Generator yielding dialog widgets
        """
        with Grid():
            yield Label("Export Format:")
            with RadioSet(id="format-select"):
                yield RadioButton("JSON", value=True)
                yield RadioButton("CSV")
                yield RadioButton("Markdown")

            yield Label("Output Path:")
            yield Input(placeholder="output.json", id="path-input")

            yield Button("Export", variant="primary", id="export-btn")
            yield Button("Cancel", variant="default", id="cancel-btn")

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """
        Handle radio button selection changes.

        Args:
            event: RadioSet changed event containing the selected button
        """
        if event.pressed.label:
            self.selected_format = event.pressed.label.lower()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button press events.

        Args:
            event: Button pressed event containing button information
        """
        if event.button.id == "export-btn":
            path_input = self.query_one("#path-input", Input)
            path = path_input.value.strip()

            if path:
                result = {
                    "format": self.selected_format,
                    "path": path,
                }
                self.dismiss(result)
            else:
                self.notify("Please enter an output path", severity="error")

        elif event.button.id == "cancel-btn":
            self.dismiss(None)
