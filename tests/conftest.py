"""Shared pytest fixtures and environment setup for Kinetic Canvas."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
import tempfile
import types
from typing import Any
import pytest

# Ensure plugin root is on sys.path
PLUGIN_ROOT = Path(__file__).parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

# Mock src.plugins.base for standalone testing if not running inside FiestaBoard
if "src.plugins.base" not in sys.modules:
    src_mod = types.ModuleType("src")
    src_plugins_mod = types.ModuleType("src.plugins")
    src_plugins_base_mod = types.ModuleType("src.plugins.base")

    @dataclass
    class PluginResult:
        available: bool
        data: dict[str, Any] | None = None
        error: str | None = None
        formatted_lines: list[str] | None = None

    class PluginBase:
        def __init__(self, manifest: dict[str, Any]):
            self._manifest = manifest
            self._config: dict[str, Any] = {}
            self._enabled = False

        @property
        def config(self) -> dict[str, Any]:
            return self._config

        @config.setter
        def config(self, value: dict[str, Any]) -> None:
            self._config = value

        @property
        def enabled(self) -> bool:
            return self._enabled

        @enabled.setter
        def enabled(self, value: bool) -> None:
            self._enabled = value

        def cleanup(self) -> None:
            pass

    src_plugins_base_mod.PluginBase = PluginBase
    src_plugins_base_mod.PluginResult = PluginResult
    src_plugins_mod.base = src_plugins_base_mod
    src_mod.plugins = src_plugins_mod

    sys.modules["src"] = src_mod
    sys.modules["src.plugins"] = src_plugins_mod
    sys.modules["src.plugins.base"] = src_plugins_base_mod


@pytest.fixture
def temp_state_file(tmp_path: Path):
    """Provide an isolated temporary state file for testing."""
    return tmp_path / ".kinetic_canvas_state_test.json"
