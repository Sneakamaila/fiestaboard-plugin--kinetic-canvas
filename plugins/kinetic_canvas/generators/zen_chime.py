"""Zen Chime & Acoustic Sculptures: Composed sound envelopes and synchronized split-flap acoustics."""

from __future__ import annotations
import math
import random
from typing import Any, Dict, List, Optional

from ..acoustics import calculate_flap_distance, get_drum_index
from ..constants import (
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_VIOLET,
    COLOR_WHITE,
    COLOR_YELLOW,
    FLAGSHIP_HEIGHT,
    FLAGSHIP_WIDTH,
    FLAP_COUNT,
    NOTE_HEIGHT,
    NOTE_WIDTH,
    PHYSICAL_FLAP_SEQUENCE,
)
from .base import GenerationResult, GeneratorBase

CHIME_MODES = ["staccato_snap", "acoustic_wave", "rainfall", "harmonic_decay"]


class ZenChimeGenerator(GeneratorBase):
    """Specifically engineers the mechanical transition to craft acoustic sound envelopes."""

    @property
    def name(self) -> str:
        return "zen_chime"

    @property
    def display_name(self) -> str:
        return "Zen Chime & Sound Sculptures (Klangpartitur)"

    def _next_code_with_delta(self, current_code: int, target_delta: int) -> int:
        """Find the exact character code that lies target_delta steps forward on the physical drum."""
        curr_idx = get_drum_index(current_code)
        target_idx = (curr_idx + target_delta) % FLAP_COUNT
        return PHYSICAL_FLAP_SEQUENCE[target_idx]

    def _generate_staccato_snap(
        self,
        prev_matrix: Optional[List[List[int]]],
        width: int,
        height: int,
    ) -> List[List[int]]:
        """Every cell advances by exactly 1 step on the drum.

        Acoustics: All modules click in unison for ~35ms, then dead silence.
        """
        grid = [[0 for _ in range(width)] for _ in range(height)]
        for r in range(height):
            for c in range(width):
                prev_code = prev_matrix[r][c] if prev_matrix else COLOR_WHITE
                grid[r][c] = self._next_code_with_delta(prev_code, 1)
        return grid

    def _generate_acoustic_wave(
        self,
        prev_matrix: Optional[List[List[int]]],
        width: int,
        height: int,
    ) -> List[List[int]]:
        """Delta increases along columns from left to right.

        Acoustics: Left columns silence immediately, sound sweeps across the board to the right.
        """
        grid = [[0 for _ in range(width)] for _ in range(height)]
        for r in range(height):
            for c in range(width):
                prev_code = prev_matrix[r][c] if prev_matrix else COLOR_BLACK
                # Column 0 has delta ~2, Column max has delta ~55
                delta = int(2 + (c / (width - 1)) * 52)
                grid[r][c] = self._next_code_with_delta(prev_code, delta)
        return grid

    def _generate_rainfall(
        self,
        prev_matrix: Optional[List[List[int]]],
        width: int,
        height: int,
        rng: random.Random,
    ) -> List[List[int]]:
        """Only 15-25% of cells advance by 1-3 steps.

        Acoustics: Sparse, delicate patter like gentle rain on a roof.
        """
        grid = [[0 for _ in range(width)] for _ in range(height)]
        for r in range(height):
            for c in range(width):
                prev_code = prev_matrix[r][c] if prev_matrix else COLOR_BLACK
                if rng.random() < 0.22:
                    delta = rng.choice([1, 2, 3])
                    grid[r][c] = self._next_code_with_delta(prev_code, delta)
                else:
                    grid[r][c] = prev_code  # Unchanged, 0 clicks
        return grid

    def _generate_harmonic_decay(
        self,
        prev_matrix: Optional[List[List[int]]],
        width: int,
        height: int,
    ) -> List[List[int]]:
        """Center has high delta (~55), perimeter has low delta (~2).

        Acoustics: Sharp initial strike, edges stop instantly while center rings out like a gong.
        """
        grid = [[0 for _ in range(width)] for _ in range(height)]
        cx = (width - 1) / 2.0
        cy = (height - 1) / 2.0
        max_dist = math.sqrt(cx**2 + cy**2)

        for r in range(height):
            for c in range(width):
                prev_code = prev_matrix[r][c] if prev_matrix else COLOR_BLACK
                dist = math.sqrt((c - cx) ** 2 + (r - cy) ** 2)
                norm_dist = min(1.0, dist / max_dist)
                # Inverted: center distance high, edges low
                delta = int(55 - norm_dist * 52)
                grid[r][c] = self._next_code_with_delta(prev_code, max(1, delta))
        return grid

    def generate(
        self,
        previous_flagship: Optional[List[List[int]]],
        previous_note: Optional[List[List[int]]],
        config: Dict[str, Any],
        state: Dict[str, Any],
    ) -> GenerationResult:
        chime_style = config.get("chime_style")
        if chime_style not in CHIME_MODES:
            # Cycle through modes
            last_mode = state.get("last_chime_mode")
            try:
                next_idx = (CHIME_MODES.index(last_mode) + 1) % len(CHIME_MODES)
                chime_style = CHIME_MODES[next_idx]
            except (ValueError, TypeError):
                chime_style = CHIME_MODES[0]

        state["last_chime_mode"] = chime_style
        rng = random.Random()

        if chime_style == "staccato_snap":
            f_grid = self._generate_staccato_snap(previous_flagship, FLAGSHIP_WIDTH, FLAGSHIP_HEIGHT)
            n_grid = self._generate_staccato_snap(previous_note, NOTE_WIDTH, NOTE_HEIGHT)
            title = "Zen Chime — Stakkato-Schlag (Δ = 1)"
            desc = "Synchroner mechanischer Peitschenschlag aller Klappen mit sofortiger Stille."
        elif chime_style == "acoustic_wave":
            f_grid = self._generate_acoustic_wave(previous_flagship, FLAGSHIP_WIDTH, FLAGSHIP_HEIGHT)
            n_grid = self._generate_acoustic_wave(previous_note, NOTE_WIDTH, NOTE_HEIGHT)
            title = "Zen Chime — Die Klangwelle (Stereo Pan)"
            desc = "Akustischer Sweep von links nach rechts durch aufsteigende Schrittdistanzen."
        elif chime_style == "rainfall":
            f_grid = self._generate_rainfall(previous_flagship, FLAGSHIP_WIDTH, FLAGSHIP_HEIGHT, rng)
            n_grid = self._generate_rainfall(previous_note, NOTE_WIDTH, NOTE_HEIGHT, rng)
            title = "Zen Chime — Mechanischer Tropfenregen"
            desc = "Feinstes, stochastisches Regentropfen-Klicken einzelner Module."
        else:  # harmonic_decay
            f_grid = self._generate_harmonic_decay(previous_flagship, FLAGSHIP_WIDTH, FLAGSHIP_HEIGHT)
            n_grid = self._generate_harmonic_decay(previous_note, NOTE_WIDTH, NOTE_HEIGHT)
            title = "Zen Chime — Resonanzglocke (Klangschale)"
            desc = "Initialer Schlag mit langem Ausklingen im Zentrum des Boards."

        return GenerationResult(
            flagship_matrix=f_grid,
            note_matrix=n_grid,
            title=title,
            description=desc,
            metadata={"chime_style": chime_style},
        )
