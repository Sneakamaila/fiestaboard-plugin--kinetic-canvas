"""Conway's Game of Life cellular automata generator for Vestaboard."""

from __future__ import annotations
import random
import time
from typing import Any, Dict, List, Optional, Tuple

from ..constants import (
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_VIOLET,
    COLOR_YELLOW,
    FLAGSHIP_HEIGHT,
    FLAGSHIP_WIDTH,
    NOTE_HEIGHT,
    NOTE_WIDTH,
)
from .base import GenerationResult, GeneratorBase


class GameOfLifeGenerator(GeneratorBase):
    """Simulates Conway's Game of Life on split-flap displays with age-based kinetic color mapping."""

    @property
    def name(self) -> str:
        return "game_of_life"

    @property
    def display_name(self) -> str:
        return "Game of Life (Zellularautomat)"

    def _count_neighbors(self, grid: List[List[int]], r: int, c: int, h: int, w: int) -> int:
        """Count live neighbors with toroidal wrap-around."""
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = (r + dr) % h
                nc = (c + dc) % w
                if grid[nr][nc] > 0:
                    count += 1
        return count

    def _step(
        self,
        grid: List[List[int]],
        h: int,
        w: int,
    ) -> Tuple[List[List[int]], int, int]:
        """Advance one generation, tracking cell age (0=dead, 1=newborn, 2+=mature).

        Returns: (new_grid, births, deaths)
        """
        new_grid = [[0 for _ in range(w)] for _ in range(h)]
        births = 0
        deaths = 0

        for r in range(h):
            for c in range(w):
                neighbors = self._count_neighbors(grid, r, c, h, w)
                is_alive = grid[r][c] > 0

                if is_alive:
                    if neighbors in (2, 3):
                        # Survives and ages
                        new_grid[r][c] = min(10, grid[r][c] + 1)
                    else:
                        # Dies
                        new_grid[r][c] = 0
                        deaths += 1
                else:
                    if neighbors == 3:
                        # Born
                        new_grid[r][c] = 1
                        births += 1

        return new_grid, births, deaths

    def _render_to_vestaboard(self, grid: List[List[int]], h: int, w: int) -> List[List[int]]:
        """Map cell state/age to Vestaboard color tiles."""
        board = [[COLOR_BLACK for _ in range(w)] for _ in range(h)]
        for r in range(h):
            for c in range(w):
                age = grid[r][c]
                if age == 0:
                    board[r][c] = COLOR_BLACK
                elif age == 1:
                    board[r][c] = COLOR_YELLOW  # Newborn
                elif age == 2:
                    board[r][c] = COLOR_GREEN   # Young
                elif age <= 4:
                    board[r][c] = COLOR_BLUE    # Mature
                elif age <= 7:
                    board[r][c] = COLOR_VIOLET  # Elder
                else:
                    board[r][c] = COLOR_RED     # Ancient immortal
        return board

    def _seed_random(self, h: int, w: int, rng: random.Random, density: float = 0.28) -> List[List[int]]:
        """Create a randomized starter grid."""
        return [
            [1 if rng.random() < density else 0 for _ in range(w)]
            for _ in range(h)
        ]

    def _grid_hash(self, grid: List[List[int]]) -> int:
        return hash(tuple(tuple(1 if cell > 0 else 0 for cell in row) for row in grid))

    def generate(
        self,
        previous_flagship: Optional[List[List[int]]],
        previous_note: Optional[List[List[int]]],
        config: Dict[str, Any],
        state: Dict[str, Any],
    ) -> GenerationResult:
        # Load or initialize simulation state
        life_state = state.get("game_of_life_state", {})
        gen = life_state.get("generation", 0)
        flagship_grid = life_state.get("flagship_grid")
        note_grid = life_state.get("note_grid")
        history = life_state.get("history", [])

        rng = random.Random()

        # Check if needs initial seed or reset due to stagnation/extinction
        needs_reseed = False
        if not flagship_grid or not note_grid:
            needs_reseed = True
        else:
            current_live = sum(sum(1 for c in row if c > 0) for row in flagship_grid)
            note_live = sum(sum(1 for c in row if c > 0) for row in note_grid)
            current_hash = self._grid_hash(flagship_grid)
            if current_live == 0 or note_live == 0 or history.count(current_hash) >= 2 or gen > 60:
                needs_reseed = True

        if needs_reseed:
            flagship_grid = self._seed_random(FLAGSHIP_HEIGHT, FLAGSHIP_WIDTH, rng, density=0.28)
            note_grid = self._seed_random(NOTE_HEIGHT, NOTE_WIDTH, rng, density=0.36)
            gen = 1
            history = [self._grid_hash(flagship_grid)]
            births = sum(sum(1 for c in row if c > 0) for row in flagship_grid)
            deaths = 0
            event_text = "Urknall / Neue Kolonie gegründet"
        else:
            flagship_grid, births, deaths = self._step(flagship_grid, FLAGSHIP_HEIGHT, FLAGSHIP_WIDTH)
            note_grid, _, _ = self._step(note_grid, NOTE_HEIGHT, NOTE_WIDTH)

            # Prevent Note from stagnating in extinction while Flagship is still alive
            note_live = sum(sum(1 for c in row if c > 0) for row in note_grid)
            if note_live < 3:
                note_grid = self._seed_random(NOTE_HEIGHT, NOTE_WIDTH, rng, density=0.36)

            gen += 1
            history.append(self._grid_hash(flagship_grid))
            if len(history) > 10:
                history.pop(0)
            event_text = f"Gen {gen}: +{births} Geburten, -{deaths} Tode"

        # Update state for next tick
        state["game_of_life_state"] = {
            "generation": gen,
            "flagship_grid": flagship_grid,
            "note_grid": note_grid,
            "history": history,
        }

        flagship_board = self._render_to_vestaboard(flagship_grid, FLAGSHIP_HEIGHT, FLAGSHIP_WIDTH)
        note_board = self._render_to_vestaboard(note_grid, NOTE_HEIGHT, NOTE_WIDTH)

        live_count = sum(sum(1 for c in row if c > 0) for row in flagship_grid)
        title = f"Conway's Game of Life — Gen #{gen}"
        description = f"{event_text} (Aktive Population: {live_count} Zellen)"

        return GenerationResult(
            flagship_matrix=flagship_board,
            note_matrix=note_board,
            title=title,
            description=description,
            metadata={"generation": gen, "live_cells": live_count, "births": births, "deaths": deaths},
        )
