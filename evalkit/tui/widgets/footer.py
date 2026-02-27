"""Footer widget for TUI."""

from textual.widgets import Footer as TextualFooter


class Footer(TextualFooter):
    """
    Custom footer widget extending Textual's Footer.

    Displays keyboard shortcuts automatically based on app bindings.
    Uses custom styling to match the TUI theme.
    """

    DEFAULT_CSS = """
    Footer {
        background: $panel;  # Match panel background of Header widget
    }
    """
