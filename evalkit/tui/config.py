"""TUI configuration module."""

from dataclasses import dataclass
from enum import Enum


class LayoutStyle(Enum):
    """TUI layout styles."""

    MINIMAL = "minimal"  # Header + primary graph only
    STANDARD = "standard"  # Header + 2x2 grid with key widgets
    FULL = "full"  # Header + 2x2 grid with all widgets


@dataclass
class TUIConfig:
    """
    Configuration for TUI appearance and behavior.

    Attributes:
        layout: Layout style (minimal, standard, or full)
        theme: Color theme (dark, light, or auto)
        show_graphs: Whether to display graph widgets
    """

    layout: LayoutStyle = LayoutStyle.FULL
    theme: str = "dark"
    show_graphs: bool = True

    @classmethod
    def from_args(cls, layout: str = "full", theme: str = "dark") -> "TUIConfig":
        """
        Create TUIConfig from CLI arguments.

        Args:
            layout: Layout style string (minimal/standard/full)
            theme: Theme string (dark/light/auto)

        Returns:
            TUIConfig instance with specified settings
        """
        layout_style = LayoutStyle(layout)
        return cls(layout=layout_style, theme=theme)
