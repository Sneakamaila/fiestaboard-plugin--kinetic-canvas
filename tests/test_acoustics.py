"""Unit tests for acoustic calculations and sound profile estimation."""

import pytest
from plugins.kinetic_canvas.acoustics import (
    calculate_flap_distance,
    compute_acoustic_score,
    get_drum_index,
    make_sparkline,
)
from plugins.kinetic_canvas.constants import (
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_WHITE,
    COLOR_YELLOW,
    FLAGSHIP_HEIGHT,
    FLAGSHIP_WIDTH,
    FLAP_COUNT,
)


def test_calculate_flap_distance_same_code():
    """Identical codes should produce 0 clicks."""
    assert calculate_flap_distance(COLOR_RED, COLOR_RED) == 0
    assert calculate_flap_distance(0, 0) == 0
    assert calculate_flap_distance(1, 1) == 0


def test_calculate_flap_distance_forward_step():
    """Consecutive codes in physical sequence should produce exact delta."""
    # Letters: A (1) to B (2) -> 1 step
    assert calculate_flap_distance(1, 2) == 1
    # Red (63) to Orange (64) -> 1 step
    assert calculate_flap_distance(COLOR_RED, COLOR_ORANGE) == 1


def test_calculate_flap_distance_wrap_around():
    """Moving backward in the drum index wraps around cyclically."""
    # B (2) to A (1) wraps full circle minus 1
    assert calculate_flap_distance(2, 1) == FLAP_COUNT - 1
    # Black (70) to Blank (0) is 1 step forward on the drum
    assert calculate_flap_distance(COLOR_BLACK, 0) == 1


def test_compute_acoustic_score_silent():
    """When target matches previous, score should be Silent with 0 clicks."""
    matrix = [[COLOR_BLACK for _ in range(FLAGSHIP_WIDTH)] for _ in range(FLAGSHIP_HEIGHT)]
    score = compute_acoustic_score(matrix, matrix)

    assert score.total_clicks == 0
    assert score.moving_modules == 0
    assert score.intensity == "Silent"
    assert score.estimated_duration_sec == 0.0


def test_compute_acoustic_score_whisper():
    """Small shifts produce Whisper intensity."""
    prev = [[COLOR_BLACK for _ in range(FLAGSHIP_WIDTH)] for _ in range(FLAGSHIP_HEIGHT)]
    curr = [[COLOR_BLACK for _ in range(FLAGSHIP_WIDTH)] for _ in range(FLAGSHIP_HEIGHT)]
    # Change only 2 modules by 1 step
    curr[0][0] = 0  # Black -> Blank is 1 step
    curr[0][1] = 0

    score = compute_acoustic_score(prev, curr)
    assert score.total_clicks == 2
    assert score.moving_modules == 2
    assert score.intensity == "Whisper"


def test_compute_acoustic_score_heavy():
    """Large shifts across all modules produce Crescendo or Thunder."""
    prev = [[1 for _ in range(FLAGSHIP_WIDTH)] for _ in range(FLAGSHIP_HEIGHT)]
    # All modules move from A (1) to 0 (Blank), which is FLAP_COUNT - 1 clicks
    curr = [[0 for _ in range(FLAGSHIP_WIDTH)] for _ in range(FLAGSHIP_HEIGHT)]

    score = compute_acoustic_score(prev, curr)
    assert score.total_clicks > 2500
    assert score.intensity == "Thunder"
    assert score.moving_modules == FLAGSHIP_WIDTH * FLAGSHIP_HEIGHT


def test_make_sparkline():
    """Sparkline should produce non-empty representation matching length of array."""
    values = [0, 5, 20, 50, 100]
    spark = make_sparkline(values)
    assert len(spark) == 5
    assert spark[0] == " "
    assert spark[-1] == "█"
