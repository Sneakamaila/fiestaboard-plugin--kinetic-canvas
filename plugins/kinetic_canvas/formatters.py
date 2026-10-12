"""String and template formatters for FiestaBoard Vestaboard displays."""

from __future__ import annotations
from typing import Any, Dict, List

from .acoustics import AcousticScore
from .constants import (
    COLOR_TAG_MAP,
    FLAGSHIP_WIDTH,
    NOTE_WIDTH,
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


def center_text(text: str, width: int) -> str:
    """Center text neatly within board width."""
    text = (text or "").strip()
    if not text:
        return " " * width if width > 0 else ""
    if len(text) >= width:
        return text[:width]
    left = (width - len(text)) // 2
    right = width - len(text) - left
    return (" " * left) + text + (" " * right)


def build_plugin_variables(
    flagship_matrix: List[List[int]],
    note_matrix: List[List[int]],
    score: AcousticScore,
    title: str,
    description: str,
    active_mode: str,
    is_quiet: bool,
    extra_metadata: Dict[str, Any],
    layout: str = "full_canvas",
) -> Dict[str, Any]:
    """Assemble the complete dictionary of variables for FiestaBoard templates."""
    raw_flagship_lines = matrix_to_lines(flagship_matrix)
    raw_note_lines = matrix_to_lines(note_matrix)

    # Determine layout lines based on layout preset
    if layout == "canvas_with_info":
        # Flagship (22x6): 4 rows art, row 5 title, row 6 acoustic sparkline + clicks
        f_lines = [
            raw_flagship_lines[0] if len(raw_flagship_lines) > 0 else "",
            raw_flagship_lines[1] if len(raw_flagship_lines) > 1 else "",
            raw_flagship_lines[2] if len(raw_flagship_lines) > 2 else "",
            raw_flagship_lines[3] if len(raw_flagship_lines) > 3 else "",
            center_text(title.upper(), FLAGSHIP_WIDTH),
            center_text(f"[{score.sparkline[:8]}] {score.total_clicks} CLKS", FLAGSHIP_WIDTH),
        ]
        # Note (15x3): 2 rows art, row 3 acoustic status
        n_lines = [
            raw_note_lines[0] if len(raw_note_lines) > 0 else "",
            raw_note_lines[1] if len(raw_note_lines) > 1 else "",
            center_text(f"{score.intensity.upper()} {score.total_clicks}C", NOTE_WIDTH),
        ]
    else:
        # full_canvas: 100% pure generative art
        f_lines = raw_flagship_lines
        n_lines = raw_note_lines

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

        # Standard Flagship lines (22x6) — dynamically formatted according to display_layout preset
        "flagship_line1": f_lines[0] if len(f_lines) > 0 else "",
        "flagship_line2": f_lines[1] if len(f_lines) > 1 else "",
        "flagship_line3": f_lines[2] if len(f_lines) > 2 else "",
        "flagship_line4": f_lines[3] if len(f_lines) > 3 else "",
        "flagship_line5": f_lines[4] if len(f_lines) > 4 else "",
        "flagship_line6": f_lines[5] if len(f_lines) > 5 else "",

        # Standard Note lines (15x3) — dynamically formatted according to display_layout preset
        "note_line1": n_lines[0] if len(n_lines) > 0 else "",
        "note_line2": n_lines[1] if len(n_lines) > 1 else "",
        "note_line3": n_lines[2] if len(n_lines) > 2 else "",

        # Raw full canvas lines (always 100% art, regardless of preset)
        "canvas_flagship_line1": raw_flagship_lines[0] if len(raw_flagship_lines) > 0 else "",
        "canvas_flagship_line2": raw_flagship_lines[1] if len(raw_flagship_lines) > 1 else "",
        "canvas_flagship_line3": raw_flagship_lines[2] if len(raw_flagship_lines) > 2 else "",
        "canvas_flagship_line4": raw_flagship_lines[3] if len(raw_flagship_lines) > 3 else "",
        "canvas_flagship_line5": raw_flagship_lines[4] if len(raw_flagship_lines) > 4 else "",
        "canvas_flagship_line6": raw_flagship_lines[5] if len(raw_flagship_lines) > 5 else "",

        "canvas_note_line1": raw_note_lines[0] if len(raw_note_lines) > 0 else "",
        "canvas_note_line2": raw_note_lines[1] if len(raw_note_lines) > 1 else "",
        "canvas_note_line3": raw_note_lines[2] if len(raw_note_lines) > 2 else "",

        # Generic line aliases (matches Note by default)
        "line1": n_lines[0] if len(n_lines) > 0 else "",
        "line2": n_lines[1] if len(n_lines) > 1 else "",
        "line3": n_lines[2] if len(n_lines) > 2 else "",
    }

    # Add extra metadata fields (e.g. weather data, generation count)
    for k, v in extra_metadata.items():
        if k not in vars_dict:
            vars_dict[f"meta_{k}"] = v

    return vars_dict
