"""Acoustic physics and kinetic sound score engine for Vestaboard split-flap displays."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .constants import (
    CODE_TO_DRUM_INDEX,
    FLAP_COUNT,
    STEP_DURATION_SEC,
)


@dataclass
class AcousticScore:
    """Detailed acoustic metrics for a transition between two board states."""
    total_clicks: int
    moving_modules: int
    max_clicks: int
    estimated_duration_sec: float
    intensity: str  # Silent, Whisper, Rainfall, Crescendo, Thunder
    sparkline: str
    center_col: float
    center_row: float
    description: str

    def to_dict(self) -> dict:
        return {
            "total_clicks": self.total_clicks,
            "moving_modules": self.moving_modules,
            "max_clicks": self.max_clicks,
            "estimated_duration_sec": round(self.estimated_duration_sec, 2),
            "intensity": self.intensity,
            "sparkline": self.sparkline,
            "center_col": round(self.center_col, 1),
            "center_row": round(self.center_row, 1),
            "description": self.description,
        }


def get_drum_index(code: int) -> int:
    """Return the sequential physical drum index for a character code."""
    return CODE_TO_DRUM_INDEX.get(code, 0)


def calculate_flap_distance(from_code: int, to_code: int) -> int:
    """Calculate the exact number of mechanical flap clicks to travel from from_code to to_code.

    Because Vestaboard split-flaps rotate strictly forward in one direction,
    the distance is cyclic: (target - start) mod FLAP_COUNT.
    """
    if from_code == to_code:
        return 0

    from_idx = get_drum_index(from_code)
    to_idx = get_drum_index(to_code)

    return (to_idx - from_idx) % FLAP_COUNT


def make_sparkline(values: List[int], min_val: int = 0, max_val: Optional[int] = None) -> str:
    """Render a sequence of integer values as an ASCII sparkline."""
    if not values:
        return ""

    bars = [" ", ".", "-", "=", "#"]
    high = max_val if max_val is not None else max(values)
    low = min_val

    if high <= low:
        return " " * len(values)

    span = high - low
    out = []
    for v in values:
        idx = int(round(((v - low) / span) * (len(bars) - 1)))
        idx = max(0, min(len(bars) - 1, idx))
        out.append(bars[idx])
    return "".join(out)


def compute_acoustic_score(
    previous_matrix: Optional[List[List[int]]],
    current_matrix: List[List[int]],
) -> AcousticScore:
    """Compute the acoustic physics and sound envelope of the transition to current_matrix."""
    rows = len(current_matrix)
    cols = len(current_matrix[0]) if rows > 0 else 0

    if rows == 0 or cols == 0:
        return AcousticScore(
            total_clicks=0,
            moving_modules=0,
            max_clicks=0,
            estimated_duration_sec=0.0,
            intensity="Silent",
            sparkline="",
            center_col=0.0,
            center_row=0.0,
            description="No modules active.",
        )

    # If no previous matrix provided, assume initial transition from all-blank (code 0)
    if previous_matrix is None or len(previous_matrix) != rows or len(previous_matrix[0]) != cols:
        previous_matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    total_clicks = 0
    moving_modules = 0
    max_clicks = 0
    col_clicks = [0 for _ in range(cols)]
    row_clicks = [0 for _ in range(rows)]

    weighted_col = 0.0
    weighted_row = 0.0

    for r in range(rows):
        for c in range(cols):
            p_code = previous_matrix[r][c]
            c_code = current_matrix[r][c]
            clicks = calculate_flap_distance(p_code, c_code)

            if clicks > 0:
                moving_modules += 1
                total_clicks += clicks
                max_clicks = max(max_clicks, clicks)
                col_clicks[c] += clicks
                row_clicks[r] += clicks
                weighted_col += c * clicks
                weighted_row += r * clicks

    if total_clicks > 0:
        center_col = weighted_col / total_clicks
        center_row = weighted_row / total_clicks
    else:
        center_col = cols / 2.0
        center_row = rows / 2.0

    estimated_duration_sec = max_clicks * STEP_DURATION_SEC

    # Classify intensity
    if total_clicks == 0:
        intensity = "Silent"
        description = "Statische Ruhe — keine Module in Bewegung."
    elif total_clicks <= 150:
        intensity = "Whisper"
        description = f"Zarte Pianissimo-Klicks ({total_clicks} Klicks, ~{estimated_duration_sec:.1f}s)."
    elif total_clicks <= 800:
        intensity = "Rainfall"
        description = f"Sanftes Regen-Prasseln ({total_clicks} Klicks, {moving_modules} Module, ~{estimated_duration_sec:.1f}s)."
    elif total_clicks <= 2500:
        intensity = "Crescendo"
        description = f"Dynamische Klangwelle ({total_clicks} Klicks, {moving_modules} Module, ~{estimated_duration_sec:.1f}s)."
    else:
        intensity = "Thunder"
        description = f"Wuchtiges Fortissimo-Rauschen ({total_clicks} Klicks, {moving_modules} Module, ~{estimated_duration_sec:.1f}s)."

    sparkline = make_sparkline(col_clicks)

    return AcousticScore(
        total_clicks=total_clicks,
        moving_modules=moving_modules,
        max_clicks=max_clicks,
        estimated_duration_sec=estimated_duration_sec,
        intensity=intensity,
        sparkline=sparkline,
        center_col=center_col,
        center_row=center_row,
        description=description,
    )
