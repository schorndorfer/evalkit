"""Dashboard layout for TUI."""

from textual.containers import Container
from textual.widget import Widget


class DashboardLayout(Container):
    """Grid layout for dashboard."""

    def __init__(self, *children: Widget) -> None:
        """
        Initialize dashboard layout.

        Args:
            *children: Child widgets to display in the grid
        """
        super().__init__(*children)

    DEFAULT_CSS = """
    DashboardLayout {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 2;
        padding: 1;
        height: 100%;
    }

    DashboardLayout > * {
        border: round $primary;
    }
    """
