"""Mondrian & De Stijl generative color field artist for Vestaboard."""

from __future__ import annotations
import random
import time
from typing import Any, Dict, List, Optional, Tuple

from ..constants import (
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_RED,
    COLOR_WHITE,
    COLOR_YELLOW,
    FLAGSHIP_HEIGHT,
    FLAGSHIP_WIDTH,
    NOTE_HEIGHT,
    NOTE_WIDTH,
)
from .base import GenerationResult, GeneratorBase


class MondrianGenerator(GeneratorBase):
    """Generates authentic De Stijl / Piet Mondrian abstract color-block compositions."""

    @property
    def name(self) -> str:
        return "mondrian"

    @property
    def display_name(self) -> str:
        return "Mondrian & De Stijl"

    def _generate_board(
        self, width: int, height: int, rng: random.Random
    ) -> List[List[int]]:
        """Procedurally divide canvas with black borders and fill rectangles with primary colors."""
        grid = [[COLOR_WHITE for _ in range(width)] for _ in range(height)]

        if width >= 20 and height >= 5:
            # Flagship (22x6): 1-2 vertical lines, 1 horizontal line
            v_lines = sorted(rng.sample(range(4, width - 4), k=rng.choice([1, 2])))
            h_lines = sorted(rng.sample(range(2, height - 2), k=rng.choice([1, 2])))
        else:
            # Note (15x3): 1 vertical line, 0-1 horizontal line
            v_lines = [rng.randint(4, width - 5)]
            h_lines = [rng.randint(1, height - 1)] if height > 2 and rng.random() > 0.4 else []

        # Find rectangular bounding boxes
        xs = [0] + v_lines + [width]
        ys = [0] + h_lines + [height]

        boxes: List[Tuple[int, int, int, int]] = []
        for i in range(len(ys) - 1):
            for j in range(len(xs) - 1):
                boxes.append((ys[i], ys[i + 1], xs[j], xs[j + 1]))

        # Primary palette: mostly white, 1 red, 1 blue, 1 yellow, occasional black block
        palette_pool = [COLOR_RED, COLOR_BLUE, COLOR_YELLOW, COLOR_BLACK]
        rng.shuffle(palette_pool)

        # Assign colors to regions
        box_colors: Dict[int, int] = {}
        for idx, _ in enumerate(boxes):
            if idx < len(palette_pool):
                box_colors[idx] = palette_pool[idx]
            else:
                box_colors[idx] = COLOR_WHITE

        # Fill regions
        for idx, (y1, y2, x1, x2) in enumerate(boxes):
            fill = box_colors[idx]
            for r in range(y1, y2):
                for c in range(x1, x2):
                    grid[r][c] = fill

        # Draw black grid lines on dividers
        for vx in v_lines:
            for r in range(height):
                grid[r][vx] = COLOR_BLACK

        for hy in h_lines:
            for c in range(width):
                grid[hy][c] = COLOR_BLACK

        return grid

    def generate(
        self,
        previous_flagship: Optional[List[List[int]]],
        previous_note: Optional[List[List[int]]],
        config: Dict[str, Any],
        state: Dict[str, Any],
    ) -> GenerationResult:
        seed = config.get("seed")
        if seed is None or seed == 0:
            seed = int(time.time() * 1000) % 1_000_000

        rng = random.Random(seed)

        flagship = self._generate_board(FLAGSHIP_WIDTH, FLAGSHIP_HEIGHT, rng)
        note = self._generate_board(NOTE_WIDTH, NOTE_HEIGHT, rng)

        title = f"Composition #{seed % 999:03d} in Rot, Gelb und Blau"
        description = "Mondrian-Komposition mit primären Farbfeldern und schwarzem Trennraster."

        return GenerationResult(
            flagship_matrix=flagship,
            note_matrix=note,
            title=title,
            description=description,
            metadata={"seed": seed, "style": "de_stijl"},
        )
