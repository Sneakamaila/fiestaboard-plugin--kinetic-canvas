"""In-memory and file-backed state management for Kinetic Canvas transitions and cellular simulations."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_CACHE_FILE = Path("/tmp/fiestaboard_kinetic_canvas_state.json")


class StateManager:
    """Manages plugin state between FiestaBoard poll intervals with persistent file-backing."""

    # Class-level shared memory ensures state survives re-instantiations within the same process
    _shared_state: Dict[str, Any] = {}

    def __init__(self, cache_file: Path = DEFAULT_CACHE_FILE) -> None:
        self.cache_file = cache_file

    def load(self) -> Dict[str, Any]:
        """Return a copy of the current state, checking shared memory first, then disk."""
        if StateManager._shared_state:
            return dict(StateManager._shared_state)

        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        StateManager._shared_state = data
                        return dict(data)
            except Exception:
                pass

        return {}

    def save(self, state: Dict[str, Any]) -> None:
        """Update both shared memory and persistent disk file."""
        StateManager._shared_state = dict(state)
        try:
            temp_file = self.cache_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(state, f)
            temp_file.replace(self.cache_file)
        except Exception:
            pass

    def clear(self) -> None:
        """Reset the shared state in memory and remove disk cache."""
        StateManager._shared_state.clear()
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except Exception:
            pass
