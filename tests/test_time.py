from datetime import timedelta

import pytest

from is_it_down.core.time import parse_history_window


def test_parse_hours() -> None:
    assert parse_history_window("24h") == timedelta(hours=24)


def test_parse_days() -> None:
    assert parse_history_window("7d") == timedelta(days=7)


def test_parse_minutes() -> None:
    assert parse_history_window("15m") == timedelta(minutes=15)


def test_parse_window_rejects_bad_values() -> None:
    with pytest.raises(ValueError):
        parse_history_window("0h")

    with pytest.raises(ValueError):
        parse_history_window("abc")

    with pytest.raises(ValueError):
        parse_history_window("10x")
