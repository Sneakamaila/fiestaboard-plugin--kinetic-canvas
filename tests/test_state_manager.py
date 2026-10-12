"""Unit tests for StateManager with persistent file backing."""

from pathlib import Path
from plugins.kinetic_canvas.state_manager import StateManager


def test_state_manager_save_and_load(tmp_path: Path):
    cache_file = tmp_path / "test_state.json"
    mgr = StateManager(cache_file=cache_file)
    mgr.clear()

    # Initial load is empty
    assert mgr.load() == {}

    # Save data
    mgr.save({"generation_count": 5, "last_cycled_mode": "mondrian"})
    loaded = mgr.load()
    assert loaded["generation_count"] == 5
    assert loaded["last_cycled_mode"] == "mondrian"

    # Mutating returned dictionary does not affect internal state
    loaded["generation_count"] = 99
    assert mgr.load()["generation_count"] == 5


def test_state_manager_clear(tmp_path: Path):
    cache_file = tmp_path / "test_state_clear.json"
    mgr = StateManager(cache_file=cache_file)
    mgr.clear()

    mgr.save({"mode": "zen_chime"})
    assert mgr.load() == {"mode": "zen_chime"}

    mgr.clear()
    assert mgr.load() == {}
