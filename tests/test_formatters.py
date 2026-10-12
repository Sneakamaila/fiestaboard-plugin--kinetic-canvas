"""Unit tests for formatters and variable builder."""

from plugins.kinetic_canvas.acoustics import AcousticScore
from plugins.kinetic_canvas.constants import (
    COLOR_BLACK,
    COLOR_RED,
    COLOR_WHITE,
    FLAGSHIP_HEIGHT,
    FLAGSHIP_WIDTH,
    NOTE_HEIGHT,
    NOTE_WIDTH,
)
from plugins.kinetic_canvas.formatters import (
    build_plugin_variables,
    code_to_token,
    matrix_to_lines,
)


def test_code_to_token():
    assert code_to_token(0) == " "
    assert code_to_token(1) == "A"
    assert code_to_token(26) == "Z"
    assert code_to_token(27) == "1"
    assert code_to_token(COLOR_RED) == "{63}"
    assert code_to_token(COLOR_BLACK) == "{70}"


def test_matrix_to_lines():
    matrix = [
        [COLOR_RED, 1, 0],
        [COLOR_WHITE, COLOR_BLACK, 2],
    ]
    lines = matrix_to_lines(matrix)
    assert len(lines) == 2
    assert lines[0] == "{63}A "
    assert lines[1] == "{69}{70}B"


def test_build_plugin_variables():
    f_mat = [[COLOR_RED for _ in range(FLAGSHIP_WIDTH)] for _ in range(FLAGSHIP_HEIGHT)]
    n_mat = [[COLOR_RED for _ in range(NOTE_WIDTH)] for _ in range(NOTE_HEIGHT)]

    score = AcousticScore(
        total_clicks=100,
        moving_modules=20,
        max_clicks=5,
        estimated_duration_sec=0.18,
        intensity="Whisper",
        sparkline=" ▂▄█ ",
        center_col=11.0,
        center_row=3.0,
        description="Test description",
    )

    data = build_plugin_variables(
        flagship_matrix=f_mat,
        note_matrix=n_mat,
        score=score,
        title="Test Title",
        description="Test Desc",
        active_mode="mondrian",
        is_quiet=False,
        extra_metadata={"custom_val": 42},
    )

    assert data["title"] == "Test Title"
    assert data["mode"] == "mondrian"
    assert data["sound_profile"] == "Whisper"
    assert data["total_clicks"] == 100
    assert data["flagship_line1"] == "{63}" * FLAGSHIP_WIDTH
    assert data["note_line1"] == "{63}" * NOTE_WIDTH
    assert data["is_quiet_hours"] == "NO"
    assert data["meta_custom_val"] == 42
