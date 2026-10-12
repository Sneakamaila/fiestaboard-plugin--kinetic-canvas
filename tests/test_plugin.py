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


def test_plugin_init(manifest_data):
    plugin = KineticCanvasPlugin(manifest_data)
    assert plugin.plugin_id == "kinetic_canvas"


def test_validate_config(manifest_data):
    plugin = KineticCanvasPlugin(manifest_data)

    # Valid config
    errors = plugin.validate_config({"mode": "mondrian", "display_layout": "full_canvas"})
    assert errors == []

    # Invalid mode
    errors = plugin.validate_config({"mode": "nonexistent_mode"})
    assert len(errors) == 1
    assert "Invalid mode" in errors[0]

    # Invalid display layout
    errors = plugin.validate_config({"display_layout": "invalid_layout"})
    assert len(errors) == 1
    assert "Invalid display_layout" in errors[0]


def test_fetch_data_mondrian(manifest_data):
    plugin = KineticCanvasPlugin(manifest_data)
    plugin.config = {
        "mode": "mondrian",
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


def test_fetch_data_cycle(manifest_data):
    plugin = KineticCanvasPlugin(manifest_data)
    plugin.config = {
        "mode": "cycle",
        "demo_mode": True,
    }

    # First fetch
    res1 = plugin.fetch_data()
    assert res1.available is True

    # Second fetch (cycles)
    res2 = plugin.fetch_data()
    assert res2.available is True
    assert res2.data["mode"] != res1.data["mode"]


def test_fetch_data_canvas_with_info(manifest_data):
    plugin = KineticCanvasPlugin(manifest_data)
    plugin.config = {
        "mode": "mondrian",
        "display_layout": "canvas_with_info",
    }

    result = plugin.fetch_data()
    assert result.available is True
    assert result.data is not None
    # Row 5 contains centered title
    assert result.data["flagship_line5"].strip() != ""
    # Row 6 contains clicks info
    assert "CLKS" in result.data["flagship_line6"]


def test_fetch_data_exception_handling(manifest_data, monkeypatch):
    plugin = KineticCanvasPlugin(manifest_data)

    def broken_generator(*args, **kwargs):
        raise RuntimeError("Simulated generator failure")

    monkeypatch.setattr("plugins.kinetic_canvas.run_generator", broken_generator)
    result = plugin.fetch_data()
    assert result.available is False
    assert "Kinetic Canvas Error" in result.error
