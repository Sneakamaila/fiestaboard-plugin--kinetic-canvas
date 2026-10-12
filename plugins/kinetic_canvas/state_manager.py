"""In-memory state management for Kinetic Canvas transitions and cellular simulations."""

from __future__ import annotations
from typing import Any, Dict


class StateManager:
    """Manages in-memory plugin state between FiestaBoard poll intervals."""

    def __init__(self) -> None:
        self._state: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Return a copy of the current in-memory state."""
        return dict(self._state)

    def save(self, state: Dict[str, Any]) -> None:
        """Update the in-memory state."""
        self._state = dict(state)

    def clear(self) -> None:
        """Reset the in-memory state."""
        self._state.clear()
