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
COLOR_BLACK = 70  # Vestaboard color code for Black chip (maps to drum index 0 on hardware)

# FiestaBoard template tags
TAG_BLANK = "{0}"
TAG_HEART = "{62}"
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
    62: TAG_HEART,
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

# Physical drum flap sequence in clockwise single-direction order (Exactly 64 flaps)
# Mechanical layout per Bit module:
# Flap 0: Blank (0)
# Flaps 1..26: Letters A-Z (1..26)
# Flaps 27..36: Numbers 1-9, 0 (27..36)
# Flaps 37..56: 20 Punctuation marks (37..42, 44, 46..50, 52..56, 59, 60, 62)
# Flaps 57..63: 7 Color chips (63..69: Red, Orange, Yellow, Green, Blue, Violet, White)
# Total: 1 + 26 + 10 + 20 + 7 = 64 physical flaps.
# White (69) advances directly to Blank (0) in 1 mechanical step (Delta = 1)!
PHYSICAL_FLAP_SEQUENCE: List[int] = [
    0,   # Blank / Black (Flap 0)
    # Letters A-Z (Flaps 1..26)
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
    # Digits 1..9, 0 (Flaps 27..36)
    27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
    # Punctuation & Icons (Flaps 37..56)
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
    62,  # ° (Flagship) / ❤️ (Note)
    # Color Chips (Flaps 57..63)
    63,  # Poppy Red
    64,  # Orange
    65,  # Yellow
    66,  # Green
    67,  # Paris Blue
    68,  # Violet
    69,  # White
]

FLAP_COUNT = len(PHYSICAL_FLAP_SEQUENCE)  # Exactly 64

# Lookup: code -> drum index (0 .. 63)
CODE_TO_DRUM_INDEX: Dict[int, int] = {
    code: idx for idx, code in enumerate(PHYSICAL_FLAP_SEQUENCE)
}
# Alias code 70 to flap 0 (Blank / Black)
CODE_TO_DRUM_INDEX[70] = 0

# Step duration per single flap click (approx 35 milliseconds in hardware)
STEP_DURATION_SEC = 0.035


def get_next_flap(code: int) -> int:
    """Return the code of the flap immediately following `code` on the physical drum wheel (Δ = 1).

    Guarantees that moving from `code` to the returned code requires strictly 1 mechanical click
    on the physical Vestaboard stepper motor (approx 35ms duration in Classic mode).
    White (69) -> Blank (0) -> 'A' (1).
    """
    idx = CODE_TO_DRUM_INDEX.get(code, 0)
    next_idx = (idx + 1) % len(PHYSICAL_FLAP_SEQUENCE)
    return PHYSICAL_FLAP_SEQUENCE[next_idx]
