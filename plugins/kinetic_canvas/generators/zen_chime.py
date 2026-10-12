"""Zen Chime & Acoustic Sculptures: Abstract color and geometric sound art for Vestaboard."""

from __future__ import annotations
import math
import random
from typing import Any, Dict, List, Optional, Tuple

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
    NOTE_HEIGHT,
    NOTE_WIDTH,
)
from .base import GenerationResult, GeneratorBase

# Color sequence on the physical drum (contiguous range: 63 to 70)
# Step distance from code to code+1 within 63..69 is strictly Δ = 1 (35ms hardware click)
COLOR_SNAP_CYCLE = [
    COLOR_RED,     # 63
    COLOR_ORANGE,  # 64
    COLOR_YELLOW,  # 65
    COLOR_GREEN,   # 66
    COLOR_BLUE,    # 67
    COLOR_VIOLET,  # 68
    COLOR_WHITE,   # 69
    COLOR_BLACK,   # 70
]

CHIME_MODES = ["staccato_snap", "acoustic_wave", "rainfall", "harmonic_decay"]


class ZenChimeGenerator(GeneratorBase):
    """Specifically engineers the mechanical transition to craft acoustic sound envelopes with abstract color art."""

    @property
    def name(self) -> str:
        return "zen_chime"

    @property
    def display_name(self) -> str:
        return "Zen Chime & Sound Sculptures"

    # ---------- 1. STACCATO SNAP: Bauhaus Geometric Color Frames (Δ = 1) ----------

    def _seed_snap_canvas(self, width: int, height: int, pattern_idx: int = 0) -> List[List[int]]:
        """Generate a geometric abstract color composition using base colors [63, 64, 65, 66]."""
        base_colors = [COLOR_RED, COLOR_ORANGE, COLOR_YELLOW, COLOR_GREEN]
        grid = [[base_colors[0] for _ in range(width)] for _ in range(height)]
        cx = (width - 1) / 2.0
        cy = (height - 1) / 2.0

        p = pattern_idx % 4
        for r in range(height):
            for c in range(width):
                if p == 0:
                    # Concentric Bauhaus frames
                    dist = math.sqrt(((c - cx) / (width / 2.0)) ** 2 + ((r - cy) / (height / 2.0)) ** 2)
                    idx = int(dist * 3.5) % len(base_colors)
                elif p == 1:
                    # Diagonal chromatic chevrons
                    idx = (c + r) % len(base_colors)
                elif p == 2:
                    # Geometric quadrants / diamond
                    dx = abs(c - cx) / (width / 2.0)
                    dy = abs(r - cy) / (height / 2.0)
                    idx = int((dx + dy) * 2.2) % len(base_colors)
                else:
                    # Symmetrical horizontal bands
                    idx = int(abs(r - cy) * 1.5) % len(base_colors)
                grid[r][c] = base_colors[idx]
        return grid

    def _generate_staccato_snap(
        self,
        prev_matrix: Optional[List[List[int]]],
        width: int,
        height: int,
        state: Dict[str, Any],
    ) -> Tuple[List[List[int]], int]:
        """Advance every color tile by exactly 1 step (Δ = 1).

        Acoustics: All modules click simultaneously in ~35ms: UNISON SNAP!
        Visual: Pure geometric color blocks shift to their adjacent harmonic hue.
        Returns: (grid, step_number)
        """
        step_key = f"snap_step_{width}x{height}"
        pat_key = f"snap_pattern_{width}x{height}"
        current_step = state.get(step_key, 0)

        # A valid snap matrix has all cells within [63..69] (strictly before 70/Black)
        is_valid_snap = (
            prev_matrix is not None
            and len(prev_matrix) == height
            and len(prev_matrix[0]) == width
            and all(63 <= cell <= 69 for row in prev_matrix for cell in row)
            and current_step < 4
        )

        if not is_valid_snap:
            # Seed a fresh geometric composition (Phase 0)
            pat = state.get(pat_key, 0)
            grid = self._seed_snap_canvas(width, height, pat)
            state[pat_key] = pat + 1
            state[step_key] = 0
            return grid, 0
        else:
            # Advance each cell by exactly 1 physical flap step in hardware
            grid = [[prev_matrix[r][c] + 1 for c in range(width)] for r in range(height)]
            next_step = current_step + 1
            state[step_key] = next_step
            return grid, next_step

    # ---------- 2. ACOUSTIC WAVE: Flowing Spectral Prism ----------

    def _generate_acoustic_wave(
        self,
        width: int,
        height: int,
        state: Dict[str, Any],
    ) -> List[List[int]]:
        """Flowing diagonal rainbow spectrum.

        Acoustics: Columns sweep and silence progressively across the display.
        Visual: Gorgeous chromatic prism of pure split-flap color tiles.
        """
        wave_key = f"wave_offset_{width}x{height}"
        wave_offset = state.get(wave_key, 0)
        grid = [[COLOR_BLACK for _ in range(width)] for _ in range(height)]

        for r in range(height):
            for c in range(width):
                # Diagonal wave bands of pure color
                color_idx = (c + r + wave_offset) % len(COLOR_SNAP_CYCLE)
                grid[r][c] = COLOR_SNAP_CYCLE[color_idx]

        state[wave_key] = (wave_offset + 2) % len(COLOR_SNAP_CYCLE)
        return grid

    # ---------- 3. MECHANICAL RAINFALL: Minimalist Night Drizzle ----------

    def _generate_rainfall(
        self,
        prev_matrix: Optional[List[List[int]]],
        width: int,
        height: int,
        rng: random.Random,
    ) -> List[List[int]]:
        """Sparse night rain on deep black with cobalt and white water droplets.

        Acoustics: Faint, delicate stochastic raindrops clicking randomly.
        Visual: Minimalist night drizzle art.
        """
        grid = [[COLOR_BLACK for _ in range(width)] for _ in range(height)]

        if prev_matrix and len(prev_matrix) == height and len(prev_matrix[0]) == width:
            for r in range(height):
                for c in range(width):
                    prev_c = prev_matrix[r][c]
                    if prev_c in [COLOR_BLUE, COLOR_WHITE]:
                        # Raindrops trickle down with 40% probability
                        if r + 1 < height and rng.random() < 0.4:
                            grid[r + 1][c] = prev_c
                        elif rng.random() < 0.3:
                            grid[r][c] = prev_c  # stay

        # Spawn new droplets at top or scattered
        for c in range(width):
            if rng.random() < 0.22:
                r = rng.randint(0, height - 1)
                grid[r][c] = rng.choice([COLOR_BLUE, COLOR_WHITE])

        return grid

    # ---------- 4. HARMONIC DECAY: Sacred Geometry / Zen Mandala ----------

    def _generate_harmonic_decay(
        self,
        width: int,
        height: int,
        state: Dict[str, Any],
    ) -> List[List[int]]:
        """Concentric radiating color mandala.

        Acoustics: Center rings vibrate with rich decay while borders remain silent.
        Visual: Meditative circular color geometry.
        """
        gong_key = f"gong_cycle_{width}x{height}"
        gong_cycle = state.get(gong_key, 0)
        cx = (width - 1) / 2.0
        cy = (height - 1) / 2.0
        grid = [[COLOR_BLACK for _ in range(width)] for _ in range(height)]

        palettes = [
            (COLOR_YELLOW, COLOR_RED, COLOR_BLUE, COLOR_BLACK),
            (COLOR_WHITE, COLOR_VIOLET, COLOR_GREEN, COLOR_BLACK),
            (COLOR_ORANGE, COLOR_YELLOW, COLOR_RED, COLOR_BLACK),
        ]
        core, mid, outer, bg = palettes[gong_cycle % len(palettes)]
        state[gong_key] = gong_cycle + 1

        for r in range(height):
            for c in range(width):
                dist = math.sqrt(((c - cx) / (width / 2.0)) ** 2 + ((r - cy) / (height / 2.0)) ** 2)
                if dist < 0.35:
                    grid[r][c] = core
                elif dist < 0.70:
                    grid[r][c] = mid
                elif dist < 1.05:
                    grid[r][c] = outer
                else:
                    grid[r][c] = bg

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
            f_grid, f_step = self._generate_staccato_snap(previous_flagship, FLAGSHIP_WIDTH, FLAGSHIP_HEIGHT, state)
            n_grid, _ = self._generate_staccato_snap(previous_note, NOTE_WIDTH, NOTE_HEIGHT, state)
            if f_step == 0:
                title = "Zen Chime — Stakkato-Setup (Geometrie)"
                desc = "Initialisiert das Bauhaus-Farbfeld. (Tipp: In FiestaBoard 'Transition' auf 'None' stellen fuer simultanen Snap)."
            else:
                title = f"Zen Chime — Stakkato-Snap #{f_step} (Delta = 1)"
                desc = "Synchroner mechanischer Peitschenschlag aller Klappen mit chromatischem Farbsprung (Delta = 1)."

        elif chime_style == "acoustic_wave":
            f_grid = self._generate_acoustic_wave(FLAGSHIP_WIDTH, FLAGSHIP_HEIGHT, state)
            n_grid = self._generate_acoustic_wave(NOTE_WIDTH, NOTE_HEIGHT, state)
            title = "Zen Chime — Die Klangwelle (Spektral-Sweep)"
            desc = "Fliessendes Farbspektrum mit mechanischem Stereo-Sweep von links nach rechts."

        elif chime_style == "rainfall":
            f_grid = self._generate_rainfall(previous_flagship, FLAGSHIP_WIDTH, FLAGSHIP_HEIGHT, rng)
            n_grid = self._generate_rainfall(previous_note, NOTE_WIDTH, NOTE_HEIGHT, rng)
            title = "Zen Chime — Tropfenregen (Nachtblau)"
            desc = "Minimalistischer Nachtregen mit sanftem, stochastischem Klick-Prasseln."

        else:  # harmonic_decay
            f_grid = self._generate_harmonic_decay(FLAGSHIP_WIDTH, FLAGSHIP_HEIGHT, state)
            n_grid = self._generate_harmonic_decay(NOTE_WIDTH, NOTE_HEIGHT, state)
            title = "Zen Chime — Resonanz-Mandala (Klangschale)"
            desc = "Zentriertes Farb-Mandala mit reicher akustischer Abklingzeit im Zentrum."

        return GenerationResult(
            flagship_matrix=f_grid,
            note_matrix=n_grid,
            title=title,
            description=desc,
            metadata={"chime_style": chime_style},
        )
