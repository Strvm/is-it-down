"""Provide functionality for `is_it_down.core.time`."""

from datetime import timedelta


def parse_history_window(raw_window: str) -> timedelta:
    """Parse history window."""
    unit = raw_window[-1]
    value_str = raw_window[:-1]
    if not value_str.isdigit():
        raise ValueError("Window must start with an integer.")

    value = int(value_str)
    if value <= 0:
        raise ValueError("Window must be greater than zero.")

    if unit == "h":
        return timedelta(hours=value)
    if unit == "d":
        return timedelta(days=value)
    if unit == "m":
        return timedelta(minutes=value)

    raise ValueError("Window must end with h, d, or m.")
