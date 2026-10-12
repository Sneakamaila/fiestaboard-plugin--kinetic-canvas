"""Unit tests for StateManager."""

import json
from pathlib import Path
from plugins.kinetic_canvas.state_manager import StateManager


def test_state_manager_save_and_load(tmp_path: Path):
    file_path = tmp_path / "state.json"
    mgr = StateManager(file_path)

    # Initial load on missing file
    data = mgr.load()
    assert data == {}

    # Save data
    mgr.save({"generation_count": 5, "last_cycled_mode": "mondrian"})

    # Verify written to disk
    assert file_path.exists()

    # Re-instantiate manager and load
    mgr2 = StateManager(file_path)
    loaded = mgr2.load()
    assert loaded["generation_count"] == 5
    assert loaded["last_cycled_mode"] == "mondrian"


def test_state_manager_corrupted_file(tmp_path: Path):
    file_path = tmp_path / "corrupted.json"
    file_path.write_text("{invalid json", encoding="utf-8")

    mgr = StateManager(file_path)
    loaded = mgr.load()
    assert loaded == {}
