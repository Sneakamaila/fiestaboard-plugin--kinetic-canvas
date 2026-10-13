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
            # Note (15x3): 1-2 vertical dividing lines, no horizontal line to avoid consuming 33% of board
            k = rng.choice([1, 2])
            v_lines = sorted(rng.sample(range(3, width - 3), k=k))
            h_lines = []

        # Find rectangular bounding boxes
        xs = [0] + v_lines + [width]
        ys = [0] + h_lines + [height]

        boxes: List[Tuple[int, int, int, int]] = []
        for i in range(len(ys) - 1):
            for j in range(len(xs) - 1):
                boxes.append((ys[i], ys[i + 1], xs[j], xs[j + 1]))

        # Authentic De Stijl palette: white canvas accented by pure red, blue, and yellow
        primaries = [COLOR_RED, COLOR_BLUE, COLOR_YELLOW]
        rng.shuffle(primaries)

        # Distribute colors: at least one primary color and white fields
        box_colors: Dict[int, int] = {}
        for idx in range(len(boxes)):
            if idx < len(primaries):
                box_colors[idx] = primaries[idx]
            else:
                box_colors[idx] = COLOR_WHITE

        # Shuffle color assignments across the boxes
        assigned = list(box_colors.values())
        rng.shuffle(assigned)
        for idx in range(len(boxes)):
            box_colors[idx] = assigned[idx]

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
