"""Quiet hours and sound dampening management for Kinetic Canvas."""

from __future__ import annotations
import datetime
from typing import Any, Dict, List, Optional, Tuple

from .constants import (
    FLAGSHIP_HEIGHT,
    FLAGSHIP_WIDTH,
    NOTE_HEIGHT,
    NOTE_WIDTH,
)


def parse_time_str(time_str: str) -> Optional[datetime.time]:
    """Parse HH:MM string to datetime.time."""
    if not time_str or ":" not in time_str:
        return None
    try:
        parts = time_str.strip().split(":")
        return datetime.time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


def is_in_quiet_hours(
    now: datetime.time,
    start: datetime.time,
    end: datetime.time,
) -> bool:
    """Check if current time is within quiet window, supporting overnight wrap-around."""
    if start <= end:
        # Same day interval (e.g. 13:00 to 15:00)
        return start <= now < end
    else:
        # Overnight interval (e.g. 22:00 to 07:00)
        return now >= start or now < end


def check_quiet_hours(
    config: Dict[str, Any],
    previous_flagship: Optional[List[List[int]]],
    previous_note: Optional[List[List[int]]],
    now: Optional[datetime.datetime] = None,
) -> Tuple[bool, Optional[List[List[int]]], Optional[List[List[int]]], str]:
    """Check if quiet hours are active and provide board matrices accordingly.

    Returns:
        (is_quiet, flagship_override, note_override, message)
    """
    if not config.get("quiet_hours_enabled", True):
        return False, None, None, "Quiet hours disabled."

    start_t = parse_time_str(config.get("quiet_hours_start", "22:00"))
    end_t = parse_time_str(config.get("quiet_hours_end", "07:00"))

    if not start_t or not end_t:
        return False, None, None, "Invalid quiet hours configuration."

    current_t = (now or datetime.datetime.now()).time()

    if not is_in_quiet_hours(current_t, start_t, end_t):
        return False, None, None, "Active hours (acoustics enabled)."

    behavior = config.get("quiet_mode_behavior", "silent_hold")

    if behavior == "blank":
        # Blank canvas
        f_override = [[0 for _ in range(FLAGSHIP_WIDTH)] for _ in range(FLAGSHIP_HEIGHT)]
        n_override = [[0 for _ in range(NOTE_WIDTH)] for _ in range(NOTE_HEIGHT)]
        msg = "Nachtruhe aktiv (Board abgedunkelt)."
        return True, f_override, n_override, msg

    # Default 'silent_hold': freeze previous matrix so exactly 0 clicks are generated
    if previous_flagship and previous_note:
        return True, previous_flagship, previous_note, "Nachtruhe aktiv (Statischer Halt, 0 Klicks)."

    # If no previous matrix yet, blank hold
    f_override = [[0 for _ in range(FLAGSHIP_WIDTH)] for _ in range(FLAGSHIP_HEIGHT)]
    n_override = [[0 for _ in range(NOTE_WIDTH)] for _ in range(NOTE_HEIGHT)]
    return True, f_override, n_override, "Nachtruhe aktiv (Stille)."
