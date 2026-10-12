"""Unit tests for generative visual and sound artists."""

import pytest
from plugins.kinetic_canvas.constants import (
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


def test_registry_cycle_mode():
    state = {}
    modes_seen = []
    for _ in range(6):
        res = run_generator("cycle", None, None, {}, state)
        modes_seen.append(res.metadata["active_mode"])

    # Cycle should rotate between different generators
    assert len(set(modes_seen)) >= 4
