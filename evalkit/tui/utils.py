"""Shared utility functions for TUI widgets."""


def get_perf_color(value: float, higher_is_better: bool = True) -> str:
    """Return a Rich color string based on performance value."""
    if not higher_is_better:
        return "cyan"  # Neutral for lower-is-better / unbounded metrics
    if value >= 0.9:
        return "bright_green"
    elif value >= 0.75:
        return "green"
    elif value >= 0.5:
        return "yellow"
    return "red"


def get_perf_label(value: float) -> str:
    """Return performance label based on value."""
    if value >= 0.9:
        return "Excellent"
    elif value >= 0.75:
        return "Good"
    elif value >= 0.5:
        return "Fair"
    return "Poor"
