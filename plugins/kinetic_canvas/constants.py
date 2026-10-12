"""Constants and Vestaboard hardware flap definitions for Kinetic Canvas."""

from __future__ import annotations
from typing import Dict, List, Tuple

# Board Dimensions
FLAGSHIP_WIDTH = 22
FLAGSHIP_HEIGHT = 6
FLAGSHIP_SIZE = FLAGSHIP_WIDTH * FLAGSHIP_HEIGHT  # 132 modules

NOTE_WIDTH = 15
NOTE_HEIGHT = 3
NOTE_SIZE = NOTE_WIDTH * NOTE_HEIGHT  # 45 modules

# Color Codes
COLOR_BLANK = 0
COLOR_RED = 63
COLOR_ORANGE = 64
COLOR_YELLOW = 65
COLOR_GREEN = 66
COLOR_BLUE = 67
COLOR_VIOLET = 68
COLOR_WHITE = 69
COLOR_BLACK = 70

# FiestaBoard template tags
TAG_BLANK = "{0}"
TAG_RED = "{63}"
TAG_ORANGE = "{64}"
TAG_YELLOW = "{65}"
TAG_GREEN = "{66}"
TAG_BLUE = "{67}"
TAG_VIOLET = "{68}"
TAG_WHITE = "{69}"
TAG_BLACK = "{70}"

COLOR_TAG_MAP: Dict[int, str] = {
    COLOR_BLANK: " ",
    COLOR_RED: TAG_RED,
    COLOR_ORANGE: TAG_ORANGE,
    COLOR_YELLOW: TAG_YELLOW,
    COLOR_GREEN: TAG_GREEN,
    COLOR_BLUE: TAG_BLUE,
    COLOR_VIOLET: TAG_VIOLET,
    COLOR_WHITE: TAG_WHITE,
    COLOR_BLACK: TAG_BLACK,
}

# Named color aliases for convenience
COLOR_NAMES: Dict[int, str] = {
    0: "blank",
    63: "red",
    64: "orange",
    65: "yellow",
    66: "green",
    67: "blue",
    68: "violet",
    69: "white",
    70: "black",
}

# Physical drum flap sequence in clockwise single-direction order
# Character codes:
# 0: Blank
# 1-26: A-Z
# 27-36: 1-9, 0
# 37-62: Punctuation marks
# 63-70: Color chips
PHYSICAL_FLAP_SEQUENCE: List[int] = [
    0,   # Blank
    # Letters A-Z (1..26)
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
    # Digits 1..9, 0 (27..36)
    27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
    # Punctuation (37..62)
    37,  # !
    38,  # @
    39,  # #
    40,  # $
    41,  # (
    42,  # )
    44,  # -
    46,  # +
    47,  # &
    48,  # =
    49,  # ;
    50,  # :
    52,  # '
    53,  # "
    54,  # %
    55,  # ,
    56,  # .
    59,  # /
    60,  # ?
    62,  # ° (or heart)
    # Colors (63..70)
    63,  # Poppy Red
    64,  # Orange
    65,  # Yellow
    66,  # Green
    67,  # Blue
    68,  # Violet
    69,  # White
    70,  # Black
]

FLAP_COUNT = len(PHYSICAL_FLAP_SEQUENCE)

# Lookup: code -> drum index (0 .. FLAP_COUNT - 1)
CODE_TO_DRUM_INDEX: Dict[int, int] = {
    code: idx for idx, code in enumerate(PHYSICAL_FLAP_SEQUENCE)
}

# Step duration per single flap click (approx 35 milliseconds in hardware)
STEP_DURATION_SEC = 0.035


def get_next_flap(code: int) -> int:
    """Return the code of the flap immediately following `code` on the physical drum wheel (Δ = 1).

    Guarantees that moving from `code` to the returned code requires strictly 1 mechanical click
    on the physical Vestaboard stepper motor (approx 35ms duration in Classic mode).
    """
    idx = CODE_TO_DRUM_INDEX.get(code, 0)
    next_idx = (idx + 1) % len(PHYSICAL_FLAP_SEQUENCE)
    return PHYSICAL_FLAP_SEQUENCE[next_idx]
