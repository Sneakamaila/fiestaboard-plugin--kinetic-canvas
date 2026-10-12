"""End-to-end unit tests for KineticCanvasPlugin."""

import json
from pathlib import Path
import pytest
from plugins.kinetic_canvas import KineticCanvasPlugin
from plugins.kinetic_canvas.state_manager import StateManager

MANIFEST_PATH = Path(__file__).parent.parent / "manifest.json"


@pytest.fixture
def manifest_data():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_plugin_init(manifest_data, temp_state_file):
    plugin = KineticCanvasPlugin(manifest_data)
    plugin.state_manager = StateManager(temp_state_file)
    assert plugin.plugin_id == "kinetic_canvas"


def test_validate_config(manifest_data):
    plugin = KineticCanvasPlugin(manifest_data)

    # Valid config
    errors = plugin.validate_config({"mode": "mondrian", "quiet_hours_start": "22:00", "quiet_hours_end": "07:00"})
    assert errors == []

    # Invalid mode
    errors = plugin.validate_config({"mode": "nonexistent_mode"})
    assert len(errors) == 1
    assert "Invalid mode" in errors[0]

    # Invalid quiet hours
    errors = plugin.validate_config({"quiet_hours_start": "25:00"})
    assert len(errors) == 1
    assert "Invalid quiet_hours_start" in errors[0]


def test_fetch_data_mondrian(manifest_data, temp_state_file):
    plugin = KineticCanvasPlugin(manifest_data)
    plugin.state_manager = StateManager(temp_state_file)
    plugin.config = {
        "mode": "mondrian",
        "quiet_hours_enabled": False,
        "seed": 1234,
    }

    result = plugin.fetch_data()
    assert result.available is True
    assert result.data is not None
    assert "Rot, Gelb und Blau" in result.data["title"]
    assert result.data["mode"] == "mondrian"
    assert result.data["total_clicks"] > 0
    assert "flagship_line1" in result.data
    assert "note_line1" in result.data


def test_fetch_data_cycle(manifest_data, temp_state_file):
    plugin = KineticCanvasPlugin(manifest_data)
    plugin.state_manager = StateManager(temp_state_file)
    plugin.config = {
        "mode": "cycle",
        "quiet_hours_enabled": False,
        "demo_mode": True,
    }

    # First fetch
    res1 = plugin.fetch_data()
    assert res1.available is True

    # Second fetch (cycles)
    res2 = plugin.fetch_data()
    assert res2.available is True
    assert res2.data["mode"] != res1.data["mode"]


def test_fetch_data_quiet_hours_active(manifest_data, temp_state_file, monkeypatch):
    import datetime
    plugin = KineticCanvasPlugin(manifest_data)
    plugin.state_manager = StateManager(temp_state_file)
    plugin.config = {
        "mode": "mondrian",
        "quiet_hours_enabled": True,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "07:00",
        "quiet_mode_behavior": "silent_hold",
    }

    # Simulate night time 23:30
    fake_now = datetime.datetime(2026, 10, 12, 23, 30)

    from plugins.kinetic_canvas import check_quiet_hours
    # Test fetch_data with check_quiet_hours patched or state pre-seeded
    plugin.state_manager.save({
        "previous_flagship": [[63 for _ in range(22)] for _ in range(6)],
        "previous_note": [[63 for _ in range(15)] for _ in range(3)],
    })

    # Mock datetime.datetime.now
    class FakeDatetime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return fake_now

    monkeypatch.setattr(datetime, "datetime", FakeDatetime)

    res = plugin.fetch_data()
    assert res.available is True
    assert res.data["is_quiet_hours"] == "YES"
    assert res.data["total_clicks"] == 0  # Absolute silence!

def test_fetch_data_exception_handling(manifest_data, temp_state_file, monkeypatch):
    plugin = KineticCanvasPlugin(manifest_data)
    plugin.state_manager = StateManager(temp_state_file)
    plugin.config = {"quiet_hours_enabled": False}

    def broken_generator(*args, **kwargs):
        raise RuntimeError("Simulated generator failure")

    monkeypatch.setattr("plugins.kinetic_canvas.run_generator", broken_generator)
    result = plugin.fetch_data()
    assert result.available is False
    assert "Kinetic Canvas Error" in result.error

