"""String and template formatters for FiestaBoard Vestaboard displays."""

from __future__ import annotations
from typing import Any, Dict, List

from .acoustics import AcousticScore
from .constants import (
    COLOR_TAG_MAP,
    PHYSICAL_FLAP_SEQUENCE,
)

# Reverse lookup: character code to printable representation
CODE_TO_CHAR: Dict[int, str] = {
    0: " ",
    # Letters 1-26
    **{i: chr(ord("A") + i - 1) for i in range(1, 27)},
    # Digits 27-36 (27='1', ..., 35='9', 36='0')
    27: "1", 28: "2", 29: "3", 30: "4", 31: "5",
    32: "6", 33: "7", 34: "8", 35: "9", 36: "0",
    # Punctuation
    37: "!", 38: "@", 39: "#", 40: "$", 41: "(", 42: ")",
    44: "-", 46: "+", 47: "&", 48: "=", 49: ";", 50: ":",
    52: "'", 53: '"', 54: "%", 55: ",", 56: ".", 59: "/",
    60: "?", 62: "°",
}


def code_to_token(code: int) -> str:
    """Convert an individual Vestaboard code into its FiestaBoard string token.

    Colors (63-70) become tags like '{63}'.
    Standard characters become single characters.
    Blank (0) becomes a single space ' '.
    """
    if code in COLOR_TAG_MAP:
        return COLOR_TAG_MAP[code]
    return CODE_TO_CHAR.get(code, " ")


def matrix_to_lines(matrix: List[List[int]]) -> List[str]:
    """Convert a 2D integer code matrix into a list of FiestaBoard line strings."""
    lines = []
    for row in matrix:
        lines.append("".join(code_to_token(code) for code in row))
    return lines


def build_plugin_variables(
    flagship_matrix: List[List[int]],
    note_matrix: List[List[int]],
    score: AcousticScore,
    title: str,
    description: str,
    active_mode: str,
    is_quiet: bool,
    extra_metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """Assemble the complete dictionary of variables for FiestaBoard templates."""
    flagship_lines = matrix_to_lines(flagship_matrix)
    note_lines = matrix_to_lines(note_matrix)

    vars_dict: Dict[str, Any] = {
        # Core titles and metadata
        "title": title,
        "mode": active_mode,
        "description": description,
        "is_quiet_hours": "YES" if is_quiet else "NO",

        # Acoustic score telemetry
        "sound_profile": score.intensity,
        "total_clicks": score.total_clicks,
        "moving_modules": score.moving_modules,
        "duration_sec": f"{score.estimated_duration_sec:.1f}s",
        "acoustic_sparkline": score.sparkline,
        "acoustic_description": score.description,

        # Flagship lines (22x6)
        "flagship_line1": flagship_lines[0] if len(flagship_lines) > 0 else "",
        "flagship_line2": flagship_lines[1] if len(flagship_lines) > 1 else "",
        "flagship_line3": flagship_lines[2] if len(flagship_lines) > 2 else "",
        "flagship_line4": flagship_lines[3] if len(flagship_lines) > 3 else "",
        "flagship_line5": flagship_lines[4] if len(flagship_lines) > 4 else "",
        "flagship_line6": flagship_lines[5] if len(flagship_lines) > 5 else "",

        # Note lines (15x3)
        "note_line1": note_lines[0] if len(note_lines) > 0 else "",
        "note_line2": note_lines[1] if len(note_lines) > 1 else "",
        "note_line3": note_lines[2] if len(note_lines) > 2 else "",

        # Generic line aliases (matches Note by default)
        "line1": note_lines[0] if len(note_lines) > 0 else "",
        "line2": note_lines[1] if len(note_lines) > 1 else "",
        "line3": note_lines[2] if len(note_lines) > 2 else "",
    }

    # Add extra metadata fields (e.g. weather data, generation count)
    for k, v in extra_metadata.items():
        if k not in vars_dict:
            vars_dict[f"meta_{k}"] = v

    return vars_dict
