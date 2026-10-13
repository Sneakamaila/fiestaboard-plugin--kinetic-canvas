"""Zen Chime & Acoustic Sculptures: Abstract color and geometric sound art for Vestaboard."""

from __future__ import annotations
import math
import random
from typing import Any, Dict, List, Optional, Tuple

from ..constants import (
    CODE_TO_DRUM_INDEX,
    COLOR_BLACK,
    COLOR_BLANK,
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
    get_next_flap,
)
from .base import GenerationResult, GeneratorBase

# Color sequence on the physical drum (contiguous range: 63 to 69 + 0)
# Step distance from code to code+1 within 63..69 is strictly Δ = 1 (35ms hardware click)
# Flap 69 (White) advances directly to Flap 0 (Blank) in 1 mechanical step (Delta = 1)!
COLOR_SNAP_CYCLE = [
    COLOR_RED,     # 63
    COLOR_ORANGE,  # 64
    COLOR_YELLOW,  # 65
    COLOR_GREEN,   # 66
    COLOR_BLUE,    # 67
    COLOR_VIOLET,  # 68
    COLOR_WHITE,   # 69
    COLOR_BLANK,   # 0 (Flap 0: natural black background)
]

CHIME_MODES = ["staccato_snap", "acoustic_wave", "rainfall", "harmonic_decay", "snap_calibration"]

CALIBRATION_STEPS: List[Tuple[int, int, str, str]] = [
    # (from_code, to_code, name_from, name_to)
    (63, 64, "Rot (63)", "Orange (64)"),
    (64, 65, "Orange (64)", "Gelb (65)"),
    (65, 66, "Gelb (65)", "Grün (66)"),
    (66, 67, "Grün (66)", "Blau (67)"),
    (67, 68, "Blau (67)", "Violett (68)"),
    (68, 69, "Violett (68)", "Weiß (69)"),
    (69, 0,  "Weiß (69)", "Schwarz / Blank (0)"),
    (0, 1,   "Schwarz / Blank (0)", "A (1)"),
    (1, 2,   "A (1)", "B (2)"),
    (2, 3,   "B (2)", "C (3)"),
    (26, 27, "Z (26)", "1 (27)"),
    (36, 37, "0 (36)", "! (37)"),
    (60, 62, "? (60)", "Herz/Grad (62)"),
    (62, 63, "Herz/Grad (62)", "Rot (63)"),
]


class ZenChimeGenerator(GeneratorBase):
    """Specifically engineers the mechanical transition to craft acoustic sound envelopes with abstract color art."""

    @property
    def name(self) -> str:
        return "zen_chime"

    @property
    def display_name(self) -> str:
        return "Zen Chime & Sound Sculptures"

    # ---------- 1. STACCATO SNAP: Physical Drum Sequences & Abstract Art (Δ = 1) ----------

    SNAP_SUITES = [
        {
            "id": "continuum",
            "name": "Ewiges Kontinuum",
            "max_steps": 999999,
            "desc": "Endlose 64-Klappen-Zirkulation ohne Reset. Jeder Takt ist ein 35ms-Unisono-Klick.",
        },
        {
            "id": "bauhaus_frames",
            "name": "Bauhaus-Farbrahmen",
            "max_steps": 7,
            "desc": "Konzentrische Farbflächen migrieren synchron von Warm nach Kalt.",
        },
        {
            "id": "chromatic_chevrons",
            "name": "Diagonale Farb-Stufen",
            "max_steps": 7,
            "desc": "Diagonale Farbstreifen wandern im Unisono-Klick durch das Farbspektrum.",
        },
        {
            "id": "heart_bloom",
            "name": "Herz-Blüte & Spektrum",
            "max_steps": 8,
            "desc": "Herz-Ikonen blühen kontinuierlich in warmes und kühles Farbspektrum auf.",
        },
        {
            "id": "color_pillars",
            "name": "Architektonische Klangsäulen",
            "max_steps": 7,
            "desc": "Vertikale Farbsäulen verschieben ihre Harmonien im mechanischen Gleichschritt.",
        },
    ]

    def _seed_snap_suite(self, suite_id_or_idx: Any, width: int, height: int) -> List[List[int]]:
        """Seed an abstract composition using strictly valid physical drum codes."""
        grid = [[COLOR_BLANK for _ in range(width)] for _ in range(height)]
        cx = (width - 1) / 2.0
        cy = (height - 1) / 2.0

        if isinstance(suite_id_or_idx, str):
            matched = [s["id"] for s in self.SNAP_SUITES if s["id"] == suite_id_or_idx]
            suite_id = matched[0] if matched else "continuum"
        else:
            suite_id = self.SNAP_SUITES[suite_id_or_idx % len(self.SNAP_SUITES)]["id"]

        if suite_id == "continuum":
            # Endless concentric bands radiating through pure color palette
            palette = [COLOR_RED, COLOR_ORANGE, COLOR_YELLOW, COLOR_GREEN, COLOR_BLUE, COLOR_VIOLET, COLOR_WHITE, COLOR_BLANK]
            for r in range(height):
                for c in range(width):
                    dist = math.sqrt(((c - cx) / (width / 2.0)) ** 2 + ((r - cy) / (height / 2.0)) ** 2)
                    p_idx = int(dist * 3.5) % len(palette)
                    grid[r][c] = palette[p_idx]

        elif suite_id == "bauhaus_frames":
            # Suite 0: Concentric Bauhaus Frame (Red outer & Orange core)
            for r in range(height):
                for c in range(width):
                    dist = math.sqrt(((c - cx) / (width / 2.0)) ** 2 + ((r - cy) / (height / 2.0)) ** 2)
                    grid[r][c] = COLOR_ORANGE if dist < 0.65 else COLOR_RED

        elif suite_id == "chromatic_chevrons":
            # Suite 1: Diagonal Chromatic Chevrons (Red & Orange)
            for r in range(height):
                for c in range(width):
                    grid[r][c] = COLOR_RED if (c + r) % 2 == 0 else COLOR_ORANGE

        elif suite_id == "heart_bloom":
            # Suite 2: Heart Blossom & Warm Spectrum (62=Heart, 63=Red, 64=Orange)
            for r in range(height):
                for c in range(width):
                    dx = abs(c - cx) / (width / 2.0)
                    dy = abs(r - cy) / (height / 2.0)
                    m_dist = dx + dy
                    if m_dist < 0.55:
                        grid[r][c] = 62  # Heart on Note / ° on Flagship
                    elif m_dist < 1.05:
                        grid[r][c] = COLOR_RED
                    else:
                        grid[r][c] = COLOR_ORANGE

        else:
            # Suite: Architectural Color Columns
            for r in range(height):
                for c in range(width):
                    grid[r][c] = COLOR_RED if (c // 2) % 2 == 0 else COLOR_ORANGE

        return grid

    def _generate_staccato_snap(
        self,
        prev_matrix: Optional[List[List[int]]],
        width: int,
        height: int,
        config: Dict[str, Any],
        state: Dict[str, Any],
    ) -> Tuple[List[List[int]], int, str, str]:
        """Advance every module strictly by 1 physical flap step on the drum wheel (Δ = 1).

        Acoustics: All modules click simultaneously in ~35ms: 100% UNISON SNAP!
        Visual: Pure geometric compositions shift harmonically along the physical drum sequence.
        Returns: (grid, step_number, suite_name, suite_desc)
        """
        step_key = f"snap_step_{width}x{height}"
        suite_key = f"snap_suite_{width}x{height}"
        pattern_cfg = config.get("snap_pattern", "continuum")

        current_step = state.get(step_key, 0)
        current_suite_idx = state.get(suite_key, 0) % len(self.SNAP_SUITES)
        active_suite = self.SNAP_SUITES[0] if pattern_cfg == "continuum" else self.SNAP_SUITES[current_suite_idx]
        max_steps = active_suite["max_steps"]
        suite_name = active_suite["name"]
        suite_desc = active_suite["desc"]

        is_valid_prev = (
            prev_matrix is not None
            and len(prev_matrix) == height
            and len(prev_matrix[0]) == width
            and all(cell in CODE_TO_DRUM_INDEX for row in prev_matrix for cell in row)
        )

        if not is_valid_prev or current_step == 0:
            # Phase 0: Setup / Movement Initializer
            seed_target = pattern_cfg if pattern_cfg != "continuum" else current_suite_idx
            grid = self._seed_snap_suite(seed_target, width, height)
            state[step_key] = 1
            return grid, 0, suite_name, suite_desc

        # Active Snap Step: Advance every single module strictly by 1 physical flap (Δ = 1)
        grid = [[get_next_flap(prev_matrix[r][c]) for c in range(width)] for r in range(height)]
        snap_num = current_step

        if pattern_cfg != "continuum" and current_step >= max_steps:
            # Suite completed its movement! Next interval will initiate the next suite
            state[step_key] = 0
            state[suite_key] = current_suite_idx + 1
        else:
            state[step_key] = current_step + 1

        return grid, snap_num, suite_name, suite_desc

    # ---------- 1B. HARDWARE CALIBRATION & FLAP-INSPECTOR ----------

    def _generate_calibration(
        self,
        width: int,
        height: int,
        state: Dict[str, Any],
    ) -> Tuple[List[List[int]], str, str]:
        """Explicit isolated step-by-step diagnostic test to verify Δ = 1 hardware clicks."""
        cal_key = f"cal_idx_{width}x{height}"
        cal_idx = state.get(cal_key, 0)
        total_steps = len(CALIBRATION_STEPS)

        if cal_idx == 0:
            # Phase 0: Initializer
            from_code, _, from_name, _ = CALIBRATION_STEPS[0]
            grid = [[from_code for _ in range(width)] for _ in range(height)]
            state[cal_key] = 1
            title = f"[Flap-Test Setup] Initialisiere {from_name}"
            desc = f"Bereitet alle {width*height} Module auf den schrittweisen Delta=1 Hardware-Test vor."
            return grid, title, desc

        step_idx = (cal_idx - 1) % total_steps
        _, to_code, from_name, to_name = CALIBRATION_STEPS[step_idx]
        grid = [[to_code for _ in range(width)] for _ in range(height)]
        state[cal_key] = cal_idx + 1

        title = f"[Flap-Test #{step_idx + 1}/{total_steps}] {from_name} -> {to_name}"
        desc = (
            f"Soll: Exakt 1 Klappen-Klick (Δ=1, 35ms) auf allen Modulen. "
            f"Falls hier eine lange Drehung erfolgt, weicht die Hardware ab."
        )
        return grid, title, desc

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
        grid = [[COLOR_BLANK for _ in range(width)] for _ in range(height)]

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
        grid = [[COLOR_BLANK for _ in range(width)] for _ in range(height)]

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
        grid = [[COLOR_BLANK for _ in range(width)] for _ in range(height)]

        palettes = [
            (COLOR_YELLOW, COLOR_RED, COLOR_BLUE, COLOR_BLANK),
            (COLOR_WHITE, COLOR_VIOLET, COLOR_GREEN, COLOR_BLANK),
            (COLOR_ORANGE, COLOR_YELLOW, COLOR_RED, COLOR_BLANK),
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
            f_grid, f_step, f_name, f_desc = self._generate_staccato_snap(previous_flagship, FLAGSHIP_WIDTH, FLAGSHIP_HEIGHT, config, state)
            n_grid, n_step, n_name, n_desc = self._generate_staccato_snap(previous_note, NOTE_WIDTH, NOTE_HEIGHT, config, state)
            step = n_step if n_step > 0 else f_step
            suite_name = n_name
            suite_desc = n_desc
            if step == 0:
                title = f"Zen Chime — Stakkato-Setup ({suite_name})"
                desc = f"Initialisiert die Startposition für synchrone Stakkato-Snaps (Delta = 1, 35ms). {suite_desc}"
            else:
                title = f"Zen Chime — Stakkato-Snap #{step} (Delta = 1)"
                desc = f"Synchroner mechanischer Peitschenschlag aller Klappen ({suite_name}, 35ms, Delta = 1). {suite_desc}"

        elif chime_style == "snap_calibration":
            f_grid, title, desc = self._generate_calibration(FLAGSHIP_WIDTH, FLAGSHIP_HEIGHT, state)
            n_grid, _, _ = self._generate_calibration(NOTE_WIDTH, NOTE_HEIGHT, state)

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
