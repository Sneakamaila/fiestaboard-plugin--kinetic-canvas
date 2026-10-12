"""State persistence manager for Kinetic Canvas transitions and cellular simulations."""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_STATE_FILE = Path(__file__).parent.parent.parent / ".kinetic_canvas_state.json"


class StateManager:
    """Manages persistent plugin state between FiestaBoard poll intervals."""

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or DEFAULT_STATE_FILE
        self._memory_state: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load state from file or return current memory state."""
        if not self.file_path or not self.file_path.exists():
            return dict(self._memory_state)

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self._memory_state.update(data)
                    return dict(self._memory_state)
        except Exception as e:
            logger.warning("Could not load Kinetic Canvas state from %s: %s", self.file_path, e)

        return dict(self._memory_state)

    def save(self, state: Dict[str, Any]) -> None:
        """Save state to memory and disk."""
        self._memory_state = dict(state)
        if not self.file_path:
            return

        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.warning("Could not persist Kinetic Canvas state to %s: %s", self.file_path, e)
