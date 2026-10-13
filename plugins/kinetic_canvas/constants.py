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

# Physical drum flap sequence in true stepper motor forward rotation direction (Exactly 64 flaps).
# Hardware Discovery: The physical stepper motors turn such that flaps cascade in descending character-code order:
# 69 (White) -> 68 (Violet) -> 67 (Blue) -> 66 (Green) -> 65 (Yellow) -> 64 (Orange) -> 63 (Red) -> 62 (Heart) -> ... -> 1 (A) -> 0 (Blank) -> 69 (White).
# Therefore:
# - Gelb (65) -> Orange (64) is strictly 1 flap step (Delta = 1)!
# - Orange (64) -> Rot (63) is strictly 1 flap step (Delta = 1)!
# - 3 (29) -> 2 (28) -> 1 (27) is strictly 1 flap step (Delta = 1)!
# - A (1) -> Blank (0) -> White (69) is strictly 1 flap step (Delta = 1)!
PHYSICAL_FLAP_SEQUENCE: List[int] = [
    # Color Chips (Flaps 0..6: White down to Red)
    69,  # White
    68,  # Violet
    67,  # Paris Blue
    66,  # Green
    65,  # Yellow (lies before Orange in physical rotation!)
    64,  # Orange (lies before Red in physical rotation!)
    63,  # Poppy Red
    # Punctuation & Icons (Flaps 7..26)
    62,  # ° (Flagship) / ❤️ (Note)
    60,  # ?
    59,  # /
    56,  # .
    55,  # ,
    54,  # %
    53,  # "
    52,  # '
    50,  # :
    49,  # ;
    48,  # =
    47,  # &
    46,  # +
    44,  # -
    42,  # )
    41,  # (
    40,  # $
    39,  # #
    38,  # @
    37,  # !
    # Digits 0, 9..1 (Flaps 27..36)
    36,  # 0
    35,  # 9
    34,  # 8
    33,  # 7
    32,  # 6
    31,  # 5
    30,  # 4
    29,  # 3 (lies before 2 in physical rotation!)
    28,  # 2 (lies before 1 in physical rotation!)
    27,  # 1
    # Letters Z down to A (Flaps 37..62)
    26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    # Blank / Black (Flap 63)
    0,   # Blank / Black (Flap 63, loops directly to Flap 0: White 69)
]

FLAP_COUNT = len(PHYSICAL_FLAP_SEQUENCE)  # Exactly 64

# Lookup: code -> drum index (0 .. 63)
CODE_TO_DRUM_INDEX: Dict[int, int] = {
    code: idx for idx, code in enumerate(PHYSICAL_FLAP_SEQUENCE)
}
# Alias code 70 to flap 0 (Blank / Black, index 63)
CODE_TO_DRUM_INDEX[70] = CODE_TO_DRUM_INDEX[0]

# Step duration per single flap click (approx 35 milliseconds in hardware)
STEP_DURATION_SEC = 0.035


def get_next_flap(code: int) -> int:
    """Return the code of the flap immediately following `code` in the physical drum rotation (Δ = 1).

    Guarantees that moving from `code` to the returned code requires strictly 1 mechanical click
    on the physical Vestaboard stepper motor (approx 35ms duration in Classic mode).
    Gelb (65) -> Orange (64) -> Rot (63) -> Herz (62) ... -> 'A' (1) -> Blank (0) -> Weiß (69).
    """
    idx = CODE_TO_DRUM_INDEX.get(code, CODE_TO_DRUM_INDEX[0])
    next_idx = (idx + 1) % len(PHYSICAL_FLAP_SEQUENCE)
    return PHYSICAL_FLAP_SEQUENCE[next_idx]
