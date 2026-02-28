"""Error dialog widget for TUI."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ErrorDialog(ModalScreen):
    """
    Modal screen displaying error messages.

    Shows a user-friendly error dialog with a title and detailed message
    to inform users when operations fail in the EvalKit TUI application.
    """

    DEFAULT_CSS = """
    ErrorDialog {
        align: center middle;
    }

    ErrorDialog > Vertical {
        background: $surface;
        border: thick $error;
        width: 60;
        height: 15;
        padding: 2;
    }

    ErrorDialog Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def __init__(self, title: str, message: str) -> None:
        """
        Initialize error dialog with title and message.

        Args:
            title: Error title to display
            message: Detailed error message
        """
        super().__init__()
        self.title = title
        self.message = message

    def compose(self) -> ComposeResult:
        """
        Compose error dialog content.

        Returns:
            Generator yielding error dialog widgets
        """
        with Vertical():
            # Create title with warning emoji
            yield Static(f"[bold red]⚠ {self.title}[/bold red]\n")

            # Display error message
            yield Static(self.message)

            yield Button("OK", variant="error", id="ok-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button press events.

        Args:
            event: Button pressed event containing button information
        """
        if event.button.id == "ok-btn":
            self.dismiss()
