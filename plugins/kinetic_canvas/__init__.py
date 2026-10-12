"""Kinetic Canvas & Acoustic Art plugin for FiestaBoard."""

from __future__ import annotations
import logging
import os
from typing import Any, Dict, List, Optional

try:
    from src.plugins.base import PluginBase, PluginResult
except ImportError:
    # Standalone compatibility fallback
    from dataclasses import dataclass

    @dataclass
    class PluginResult:
        available: bool
        data: dict[str, Any] | None = None
        error: str | None = None
        formatted_lines: list[str] | None = None

    class PluginBase:  # type: ignore[no-redef]
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

from .acoustics import compute_acoustic_score
from .constants import (
    FLAGSHIP_HEIGHT,
    FLAGSHIP_WIDTH,
    NOTE_HEIGHT,
    NOTE_WIDTH,
)
from .formatters import build_plugin_variables
from .generators.registry import AVAILABLE_GENERATORS, run_generator
from .quiet_hours import check_quiet_hours, parse_time_str
from .state_manager import StateManager

logger = logging.getLogger(__name__)


class KineticCanvasPlugin(PluginBase):
    """Abstract generative art and kinetic acoustic soundscape plugin for Vestaboards."""

    def __init__(self, manifest: Dict[str, Any]):
        super().__init__(manifest)
        self.state_manager = StateManager()

    @property
    def plugin_id(self) -> str:
        return "kinetic_canvas"

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate user configuration settings."""
        errors: List[str] = []
        mode = (config.get("mode") or "cycle").lower().strip()
        valid_modes = list(AVAILABLE_GENERATORS.keys()) + ["cycle", "auto", "exhibition"]

        if mode not in valid_modes:
            errors.append(f"Invalid mode '{mode}'. Choose from: {', '.join(valid_modes)}")

        layout = (config.get("display_layout") or "full_canvas").lower().strip()
        if layout not in ("full_canvas", "canvas_with_info"):
            errors.append(f"Invalid display_layout '{layout}'. Choose 'full_canvas' or 'canvas_with_info'.")

        if config.get("quiet_hours_enabled", True):
            start = config.get("quiet_hours_start", "22:00")
            end = config.get("quiet_hours_end", "07:00")
            if not parse_time_str(start):
                errors.append(f"Invalid quiet_hours_start '{start}'. Must be HH:MM format.")
            if not parse_time_str(end):
                errors.append(f"Invalid quiet_hours_end '{end}'. Must be HH:MM format.")

        return errors

    def fetch_data(self) -> PluginResult:
        """Generate the next kinetic canvas composition and compute acoustic score."""
        cfg = self.config or {}

        try:
            state = self.state_manager.load()
            prev_flagship = state.get("previous_flagship")
            prev_note = state.get("previous_note")

            # 1. Quiet Hours Check
            is_quiet, f_override, n_override, quiet_msg = check_quiet_hours(
                cfg, prev_flagship, prev_note
            )

            if is_quiet and f_override is not None and n_override is not None:
                # Calculate acoustic score for override (typically 0 clicks for silent hold)
                score = compute_acoustic_score(prev_flagship, f_override)

                # Persist state
                state["previous_flagship"] = f_override
                state["previous_note"] = n_override
                self.state_manager.save(state)

                data = build_plugin_variables(
                    flagship_matrix=f_override,
                    note_matrix=n_override,
                    score=score,
                    title="Nachtruhe (Stille)",
                    description=quiet_msg,
                    active_mode="quiet_hours",
                    is_quiet=True,
                    extra_metadata={},
                )
                return PluginResult(available=True, data=data)

            # 2. Active Mode Generation
            mode = cfg.get("mode", "cycle")
            result = run_generator(mode, prev_flagship, prev_note, cfg, state)

            # 3. Acoustic Physics Computation
            score = compute_acoustic_score(prev_flagship, result.flagship_matrix)

            # 4. State Persistence
            state["previous_flagship"] = result.flagship_matrix
            state["previous_note"] = result.note_matrix
            state["generation_count"] = state.get("generation_count", 0) + 1
            self.state_manager.save(state)

            # 5. Build Template Variables
            layout = cfg.get("display_layout", "full_canvas")
            data = build_plugin_variables(
                flagship_matrix=result.flagship_matrix,
                note_matrix=result.note_matrix,
                score=score,
                title=result.title,
                description=result.description,
                active_mode=result.metadata.get("active_mode", mode),
                is_quiet=False,
                extra_metadata=result.metadata,
                layout=layout,
            )

            return PluginResult(available=True, data=data)

        except Exception as e:
            logger.exception("Unexpected error in KineticCanvasPlugin")
            return PluginResult(available=False, error=f"Kinetic Canvas Error: {e}")
