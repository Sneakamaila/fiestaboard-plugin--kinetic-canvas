"""Unit tests for in-memory StateManager."""

from plugins.kinetic_canvas.state_manager import StateManager


def test_state_manager_save_and_load():
    mgr = StateManager()

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


def test_state_manager_clear():
    mgr = StateManager()
    mgr.save({"mode": "zen_chime"})
    assert mgr.load() == {"mode": "zen_chime"}

    mgr.clear()
    assert mgr.load() == {}
