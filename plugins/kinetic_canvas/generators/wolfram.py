"""Wolfram 1D elementary cellular automata tapestry generator for Vestaboard."""

from __future__ import annotations
import random
from typing import Any, Dict, List, Optional

from ..constants import (
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_WHITE,
    COLOR_YELLOW,
    FLAGSHIP_HEIGHT,
    FLAGSHIP_WIDTH,
    NOTE_HEIGHT,
    NOTE_WIDTH,
)
from .base import GenerationResult, GeneratorBase

# Popular Wolfram rules with distinct visual/mathematical characteristics
DEFAULT_RULES = [30, 90, 110, 184]
RULE_PALETTES = {
    30: (COLOR_RED, COLOR_ORANGE),      # Chaotic / turbulent (Poppy red / orange)
    90: (COLOR_BLUE, COLOR_WHITE),      # Sierpinski fractal (Blue / white)
    110: (COLOR_GREEN, COLOR_YELLOW),   # Universal Turing-complete (Green / yellow)
    184: (COLOR_YELLOW, COLOR_BLUE),    # Traffic flow / surface growth (Yellow / blue)
}


class WolframAutomataGenerator(GeneratorBase):
    """Generates continuous scrolling 1D cellular automata tapestries (Rule 30, 90, 110, 184)."""

    @property
    def name(self) -> str:
        return "wolfram"

    @property
    def display_name(self) -> str:
        return "Wolfram Automata (Regel 30/90/110)"

    def _apply_rule(self, state: List[int], rule: int) -> List[int]:
        """Compute the next 1D generation from state under the given Wolfram rule number."""
        n = len(state)
        next_gen = [0 for _ in range(n)]
        for i in range(n):
            left = state[(i - 1) % n]
            center = state[i]
            right = state[(i + 1) % n]
            pattern = (left << 2) | (center << 1) | right
            next_gen[i] = (rule >> pattern) & 1
        return next_gen

    def generate(
        self,
        previous_flagship: Optional[List[List[int]]],
        previous_note: Optional[List[List[int]]],
        config: Dict[str, Any],
        state: Dict[str, Any],
    ) -> GenerationResult:
        rule_num = config.get("wolfram_rule")
        if rule_num not in [30, 90, 110, 184]:
            rule_num = 30  # Default to chaotic Rule 30

        primary_color, secondary_color = RULE_PALETTES.get(
            rule_num, (COLOR_GREEN, COLOR_YELLOW)
        )

        wolfram_state = state.get("wolfram_state", {})
        current_rule = wolfram_state.get("rule", rule_num)
        flagship_rows = wolfram_state.get("flagship_rows")
        note_rows = wolfram_state.get("note_rows")
        step_count = wolfram_state.get("step_count", 0)

        # Re-seed if rule changed or initial run
        if current_rule != rule_num or not flagship_rows or not note_rows:
            # Seed with a single center impulse
            f_seed = [0] * FLAGSHIP_WIDTH
            f_seed[FLAGSHIP_WIDTH // 2] = 1

            flagship_rows = [f_seed]
            for _ in range(FLAGSHIP_HEIGHT - 1):
                flagship_rows.append(self._apply_rule(flagship_rows[-1], rule_num))

            n_seed = [0] * NOTE_WIDTH
            n_seed[NOTE_WIDTH // 2] = 1
            note_rows = [n_seed]
            for _ in range(NOTE_HEIGHT - 1):
                note_rows.append(self._apply_rule(note_rows[-1], rule_num))

            step_count = FLAGSHIP_HEIGHT
        else:
            # Advance: calculate new bottom row and scroll
            next_f = self._apply_rule(flagship_rows[-1], rule_num)
            flagship_rows = flagship_rows[1:] + [next_f]

            next_n = self._apply_rule(note_rows[-1], rule_num)
            note_rows = note_rows[1:] + [next_n]

            step_count += 1

        state["wolfram_state"] = {
            "rule": rule_num,
            "flagship_rows": flagship_rows,
            "note_rows": note_rows,
            "step_count": step_count,
        }

        # Render rows to board colors
        flagship_matrix = [
            [
                primary_color if cell == 1 else COLOR_BLACK
                for cell in row
            ]
            for row in flagship_rows
        ]
        note_matrix = [
            [
                primary_color if cell == 1 else COLOR_BLACK
                for cell in row
            ]
            for row in note_rows
        ]

        title = f"Wolfram-Automat — Regel {rule_num} (Schritt {step_count})"
        description = f"1D-Zellularautomat nach Stephen Wolfram (Regel {rule_num}), kinetisch gescrollt."

        return GenerationResult(
            flagship_matrix=flagship_matrix,
            note_matrix=note_matrix,
            title=title,
            description=description,
            metadata={"rule": rule_num, "step": step_count},
        )
