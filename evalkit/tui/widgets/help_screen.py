"""Help screen widget for TUI."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from rich.table import Table


class HelpScreen(ModalScreen):
    """
    Modal screen displaying keyboard shortcuts.

    Shows a table of available keyboard shortcuts and their descriptions
    to help users navigate the EvalKit TUI application.
    """

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    HelpScreen > Vertical {
        background: $surface;
        border: thick $primary;
        width: 60;
        height: 25;
        padding: 2;
    }

    HelpScreen Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """
        Compose help screen content.

        Returns:
            Generator yielding help screen widgets
        """
        with Vertical():
            # Create title
            yield Static("# EvalKit Keyboard Shortcuts\n")

            # Create shortcuts table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Key", style="cyan", width=15)
            table.add_column("Action", style="white", width=30)

            # Add keyboard shortcuts
            table.add_row("q / Ctrl+C", "Quit application")
            table.add_row("h / ?", "Show this help")
            table.add_row("e", "Export results")
            table.add_row("Tab", "Focus next panel")
            table.add_row("Shift+Tab", "Focus previous panel")
            table.add_row("↑ ↓ ← →", "Navigate/scroll")

            yield Static(table)
            yield Button("Close", variant="primary", id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button press events.

        Args:
            event: Button pressed event containing button information
        """
        if event.button.id == "close-btn":
            self.dismiss()
