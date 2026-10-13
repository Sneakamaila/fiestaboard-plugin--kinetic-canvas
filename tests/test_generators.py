"""Unit tests for generative visual and sound artists."""

import pytest
from plugins.kinetic_canvas.constants import (
    CODE_TO_DRUM_INDEX,
    COLOR_BLACK,
    COLOR_WHITE,
    FLAGSHIP_HEIGHT,
    FLAGSHIP_WIDTH,
    NOTE_HEIGHT,
    NOTE_WIDTH,
)
from plugins.kinetic_canvas.generators.cellular import GameOfLifeGenerator
from plugins.kinetic_canvas.generators.mondrian import MondrianGenerator
from plugins.kinetic_canvas.generators.registry import (
    AVAILABLE_GENERATORS,
    get_generator,
    run_generator,
)
from plugins.kinetic_canvas.generators.weather import WeatherResonanceGenerator
from plugins.kinetic_canvas.generators.wolfram import WolframAutomataGenerator
from plugins.kinetic_canvas.generators.zen_chime import ZenChimeGenerator


def test_mondrian_dimensions_and_output():
    gen = MondrianGenerator()
    res = gen.generate(None, None, {"seed": 42}, {})

    assert len(res.flagship_matrix) == FLAGSHIP_HEIGHT
    assert len(res.flagship_matrix[0]) == FLAGSHIP_WIDTH
    assert len(res.note_matrix) == NOTE_HEIGHT
    assert len(res.note_matrix[0]) == NOTE_WIDTH
    assert "Mondrian" in res.description or "Rot" in res.title


def test_game_of_life_evolution():
    gen = GameOfLifeGenerator()
    state = {}
    # Generation 1
    res1 = gen.generate(None, None, {}, state)
    assert res1.metadata["generation"] == 1
    assert "game_of_life_state" in state

    # Generation 2
    res2 = gen.generate(res1.flagship_matrix, res1.note_matrix, {}, state)
    assert res2.metadata["generation"] == 2
    assert len(res2.flagship_matrix) == FLAGSHIP_HEIGHT
    assert len(res2.flagship_matrix[0]) == FLAGSHIP_WIDTH


def test_wolfram_automata():
    gen = WolframAutomataGenerator()
    state = {}
    res = gen.generate(None, None, {"wolfram_rule": 30}, state)

    assert len(res.flagship_matrix) == FLAGSHIP_HEIGHT
    assert len(res.flagship_matrix[0]) == FLAGSHIP_WIDTH
    assert res.metadata["rule"] == 30

    # Step again to verify scroll
    res2 = gen.generate(res.flagship_matrix, res.note_matrix, {"wolfram_rule": 30}, state)
    assert res2.metadata["step"] == FLAGSHIP_HEIGHT + 1


def test_weather_resonance_demo_mode():
    gen = WeatherResonanceGenerator()
    config = {"demo_mode": True, "city_name": "Teststadt"}
    res = gen.generate(None, None, config, {})

    assert len(res.flagship_matrix) == FLAGSHIP_HEIGHT
    assert len(res.flagship_matrix[0]) == FLAGSHIP_WIDTH
    assert "Teststadt" in res.title
    assert "temperature" in res.metadata


def test_zen_chime_staccato_snap():
    gen = ZenChimeGenerator()
    prev = [[COLOR_WHITE for _ in range(FLAGSHIP_WIDTH)] for _ in range(FLAGSHIP_HEIGHT)]
    prev_note = [[COLOR_WHITE for _ in range(NOTE_WIDTH)] for _ in range(NOTE_HEIGHT)]

    res = gen.generate(prev, prev_note, {"chime_style": "staccato_snap"}, {})
    assert "Stakkato" in res.title
    assert len(res.flagship_matrix) == FLAGSHIP_HEIGHT
    assert len(res.flagship_matrix[0]) == FLAGSHIP_WIDTH


def test_zen_chime_all_styles():
    gen = ZenChimeGenerator()
    for style in ["staccato_snap", "acoustic_wave", "rainfall", "harmonic_decay"]:
        res = gen.generate(None, None, {"chime_style": style}, {})
        assert len(res.flagship_matrix) == FLAGSHIP_HEIGHT
        assert res.metadata["chime_style"] == style


def test_zen_chime_snap_unison_physics():
    """Verify that a consecutive snap transition yields max_clicks == 1 for all 132 modules."""
    from plugins.kinetic_canvas.acoustics import compute_acoustic_score

    gen = ZenChimeGenerator()
    state = {}
    # Turn 1: Setup phase
    res1 = gen.generate(None, None, {"chime_style": "staccato_snap"}, state)
    # Turn 2: Snap #1 (every tile advances by exactly 1 step)
    res2 = gen.generate(res1.flagship_matrix, res1.note_matrix, {"chime_style": "staccato_snap"}, state)

    score = compute_acoustic_score(res1.flagship_matrix, res2.flagship_matrix)
    assert score.max_clicks == 1
    assert score.total_clicks == FLAGSHIP_WIDTH * FLAGSHIP_HEIGHT
    assert score.moving_modules == FLAGSHIP_WIDTH * FLAGSHIP_HEIGHT
    assert score.intensity == "Snap"
    assert "Peitschenschlag" in score.description


def test_zen_chime_pure_color_no_letters():
    """Ensure Zen Chime uses only colors (63..70) or blank (0), and never plain letters (1..26)."""
    gen = ZenChimeGenerator()
    state = {}
    for style in ["staccato_snap", "acoustic_wave", "rainfall", "harmonic_decay"]:
        res = gen.generate(None, None, {"chime_style": style}, state)
        for row in res.flagship_matrix:
            for code in row:
                # Must be color (63..70) or blank (0)
                assert code == 0 or 63 <= code <= 70, f"Found illegal character code {code} in {style}"


def test_direct_zen_mode_aliases():
    """Ensure zen_snap, zen_wave, zen_rain, zen_gong invoke the correct sound profile directly."""
    for alias, expected_style in [
        ("zen_snap", "staccato_snap"),
        ("zen_wave", "acoustic_wave"),
        ("zen_rain", "rainfall"),
        ("zen_gong", "harmonic_decay"),
    ]:
        res = run_generator(alias, None, None, {}, {})
        assert res.metadata["active_mode"] == alias
        assert res.metadata["chime_style"] == expected_style


def test_registry_cycle_mode():
    state = {}
    modes_seen = []
    for _ in range(6):
        res = run_generator("cycle", None, None, {}, state)
        modes_seen.append(res.metadata["active_mode"])

    # Cycle should rotate between different generators
    assert len(set(modes_seen)) >= 4


def test_zen_chime_note_snap_all_consecutive_steps():
    """Verify that on Vestaboard Note (15x3), every step in Suite 0 advances strictly with Delta = 1."""
    from plugins.kinetic_canvas.acoustics import calculate_flap_distance, compute_acoustic_score

    gen = ZenChimeGenerator()
    state = {}

    # Step 0: Setup / Movement Initializer
    res = gen.generate(None, None, {"chime_style": "staccato_snap"}, state)
    prev_note = res.note_matrix

    # Steps 1 to 7: All 7 snaps must have Δ = 1 for all 45 modules
    for step_num in range(1, 8):
        res = gen.generate(res.flagship_matrix, prev_note, {"chime_style": "staccato_snap"}, state)
        curr_note = res.note_matrix

        score = compute_acoustic_score(prev_note, curr_note)
        assert score.max_clicks == 1, f"Step {step_num} failed max_clicks == 1 (got {score.max_clicks})"
        assert score.total_clicks == NOTE_WIDTH * NOTE_HEIGHT  # exactly 45 clicks
        assert score.moving_modules == NOTE_WIDTH * NOTE_HEIGHT  # exactly 45 modules

        for r in range(NOTE_HEIGHT):
            for c in range(NOTE_WIDTH):
                dist = calculate_flap_distance(prev_note[r][c], curr_note[r][c])
                assert dist == 1, f"Cell ({r}, {c}) at step {step_num} had distance {dist}"

        prev_note = curr_note


def test_zen_continuum_infinite_snap_64_steps():
    """Verify that in Continuum mode, Staccato Snap performs 64 uninterrupted Delta=1 clicks without reset."""
    from plugins.kinetic_canvas.acoustics import calculate_flap_distance, compute_acoustic_score

    gen = ZenChimeGenerator()
    state = {}

    # Initializer
    res = gen.generate(None, None, {"chime_style": "staccato_snap", "snap_pattern": "continuum"}, state)
    prev_note = res.note_matrix
    prev_flagship = res.flagship_matrix

    # Test full 64-step circle: EVERY transition must be Δ = 1
    for step_num in range(1, 65):
        res = gen.generate(prev_flagship, prev_note, {"chime_style": "staccato_snap", "snap_pattern": "continuum"}, state)
        curr_note = res.note_matrix
        curr_flagship = res.flagship_matrix

        score = compute_acoustic_score(prev_note, curr_note)
        assert score.max_clicks == 1, f"Step {step_num} failed max_clicks == 1 (got {score.max_clicks})"
        assert score.moving_modules == NOTE_WIDTH * NOTE_HEIGHT
        assert score.total_clicks == NOTE_WIDTH * NOTE_HEIGHT

        for r in range(NOTE_HEIGHT):
            for c in range(NOTE_WIDTH):
                dist = calculate_flap_distance(prev_note[r][c], curr_note[r][c])
                assert dist == 1, f"Cell ({r}, {c}) at step {step_num} had distance {dist}"

        prev_note = curr_note
        prev_flagship = curr_flagship


def test_zen_snap_calibration_mode():
    """Verify that snap_calibration mode cycles through all isolated diagnostic steps with clear labels."""
    from plugins.kinetic_canvas.acoustics import calculate_flap_distance
    from plugins.kinetic_canvas.generators.zen_chime import CALIBRATION_STEPS

    gen = ZenChimeGenerator()
    state = {}

    # Step 0: Setup
    res0 = gen.generate(None, None, {"chime_style": "snap_calibration"}, state)
    assert "[Flap-Test Setup]" in res0.title
    prev_note = res0.note_matrix

    # Step 1: Gelb (65) -> Orange (64)
    res1 = gen.generate(res0.flagship_matrix, prev_note, {"chime_style": "snap_calibration"}, state)
    assert "[Flap-Test #1/" in res1.title
    assert "Gelb (65) -> Orange (64)" in res1.title
    assert res1.note_matrix[0][0] == 64
    assert calculate_flap_distance(prev_note[0][0], res1.note_matrix[0][0]) == 1


def test_get_next_flap_cyclic_accuracy():
    """Verify physical flap successor behavior at wrap boundaries and color sectors."""
    from plugins.kinetic_canvas.constants import get_next_flap

    # True physical rotation direction
    assert get_next_flap(65) == 64  # Yellow -> Orange
    assert get_next_flap(64) == 63  # Orange -> Red
    assert get_next_flap(63) == 62  # Red -> Heart / Degree
    assert get_next_flap(1) == 0    # 'A' -> Blank
    assert get_next_flap(0) == 69   # Blank -> White (Physical wrap around to flap 0: White!)
    assert get_next_flap(70) == 69  # Code 70 alias maps to Blank -> White
    assert get_next_flap(27) == 26  # '1' -> 'Z'
    assert get_next_flap(37) == 36  # '!' -> '0'


def test_mondrian_note_layout_no_horizontal_lines():
    """Verify that on Note (15x3), Mondrian generates clean vertical color blocks without horizontal lines."""
    gen = MondrianGenerator()
    import random
    rng = random.Random(42)
    grid = gen._generate_board(NOTE_WIDTH, NOTE_HEIGHT, rng)

    # No row should be completely black
    for r in range(NOTE_HEIGHT):
        row = grid[r]
        assert not all(c == COLOR_BLACK for c in row), f"Row {r} on Note was completely black"

    # Must contain at least one primary color (Red, Blue, or Yellow)
    all_codes = {c for row in grid for c in row}
    from plugins.kinetic_canvas.constants import COLOR_RED, COLOR_BLUE, COLOR_YELLOW
    assert any(c in all_codes for c in (COLOR_RED, COLOR_BLUE, COLOR_YELLOW))


def test_game_of_life_note_never_stays_extinct():
    """Verify that Game of Life maintains living cells on Note across 25 generations."""
    gen = GameOfLifeGenerator()
    state = {}
    prev_f = None
    prev_n = None

    for _ in range(25):
        res = gen.generate(prev_f, prev_n, {}, state)
        note_live = sum(sum(1 for c in row if c != COLOR_BLACK) for row in res.note_matrix)
        assert note_live >= 3, "Game of Life Note went extinct / below minimum threshold"
        prev_f = res.flagship_matrix
        prev_n = res.note_matrix


def test_wolfram_rule_184_traffic_particles():
    """Verify Rule 184 starts with distributed traffic particles instead of a solitary dot."""
    gen = WolframAutomataGenerator()
    state = {}
    res = gen.generate(None, None, {"wolfram_rule": 184}, state)
    note_live = sum(sum(1 for c in row if c != COLOR_BLACK) for row in res.note_matrix)
    # 3 rows of 15 cells: with density ~0.4, should have well over 5 live particles
    assert note_live >= 6, f"Rule 184 had too few particles on Note: {note_live}"

