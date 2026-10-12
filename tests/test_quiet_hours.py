"""Unit tests for quiet hours and night silencing."""

import datetime
import pytest
from plugins.kinetic_canvas.constants import (
    COLOR_BLUE,
    FLAGSHIP_HEIGHT,
    FLAGSHIP_WIDTH,
    NOTE_HEIGHT,
    NOTE_WIDTH,
)
from plugins.kinetic_canvas.quiet_hours import (
    check_quiet_hours,
    is_in_quiet_hours,
    parse_time_str,
)


def test_parse_time_str():
    assert parse_time_str("22:00") == datetime.time(22, 0)
    assert parse_time_str("07:30") == datetime.time(7, 30)
    assert parse_time_str("invalid") is None
    assert parse_time_str("") is None


def test_is_in_quiet_hours_overnight():
    start = datetime.time(22, 0)
    end = datetime.time(7, 0)

    # 23:30 is in quiet window
    assert is_in_quiet_hours(datetime.time(23, 30), start, end) is True
    # 02:15 is in quiet window
    assert is_in_quiet_hours(datetime.time(2, 15), start, end) is True
    # 07:00 is end (active)
    assert is_in_quiet_hours(datetime.time(7, 0), start, end) is False
    # 14:00 is active day
    assert is_in_quiet_hours(datetime.time(14, 0), start, end) is False


def test_is_in_quiet_hours_daytime():
    start = datetime.time(13, 0)
    end = datetime.time(15, 0)

    assert is_in_quiet_hours(datetime.time(13, 30), start, end) is True
    assert is_in_quiet_hours(datetime.time(12, 59), start, end) is False
    assert is_in_quiet_hours(datetime.time(15, 0), start, end) is False


def test_check_quiet_hours_silent_hold():
    prev_f = [[COLOR_BLUE for _ in range(FLAGSHIP_WIDTH)] for _ in range(FLAGSHIP_HEIGHT)]
    prev_n = [[COLOR_BLUE for _ in range(NOTE_WIDTH)] for _ in range(NOTE_HEIGHT)]

    cfg = {
        "quiet_hours_enabled": True,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "07:00",
        "quiet_mode_behavior": "silent_hold",
    }
    night_time = datetime.datetime(2026, 10, 12, 23, 30)

    is_quiet, f_out, n_out, msg = check_quiet_hours(cfg, prev_f, prev_n, now=night_time)
    assert is_quiet is True
    # silent_hold returns exact previous matrices
    assert f_out == prev_f
    assert n_out == prev_n
    assert "0 Klicks" in msg


def test_check_quiet_hours_blank():
    prev_f = [[COLOR_BLUE for _ in range(FLAGSHIP_WIDTH)] for _ in range(FLAGSHIP_HEIGHT)]
    prev_n = [[COLOR_BLUE for _ in range(NOTE_WIDTH)] for _ in range(NOTE_HEIGHT)]

    cfg = {
        "quiet_hours_enabled": True,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "07:00",
        "quiet_mode_behavior": "blank",
    }
    night_time = datetime.datetime(2026, 10, 12, 23, 30)

    is_quiet, f_out, n_out, msg = check_quiet_hours(cfg, prev_f, prev_n, now=night_time)
    assert is_quiet is True
    # blank returns all 0s
    assert f_out[0][0] == 0
    assert "abgedunkelt" in msg
