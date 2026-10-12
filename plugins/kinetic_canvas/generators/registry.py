"""Registry and cycle manager for Kinetic Canvas visual generators."""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .base import GenerationResult, GeneratorBase
from .cellular import GameOfLifeGenerator
from .mondrian import MondrianGenerator
from .weather import WeatherResonanceGenerator
from .wolfram import WolframAutomataGenerator
from .zen_chime import ZenChimeGenerator

AVAILABLE_GENERATORS: Dict[str, GeneratorBase] = {
    "mondrian": MondrianGenerator(),
    "game_of_life": GameOfLifeGenerator(),
    "wolfram": WolframAutomataGenerator(),
    "weather": WeatherResonanceGenerator(),
    "zen_chime": ZenChimeGenerator(),
}

CYCLE_SEQUENCE = ["mondrian", "game_of_life", "weather", "zen_chime", "wolfram"]


def get_generator(mode: str) -> Optional[GeneratorBase]:
    """Retrieve generator instance by id."""
    return AVAILABLE_GENERATORS.get(mode)


def run_generator(
    mode: str,
    previous_flagship: Optional[List[List[int]]],
    previous_note: Optional[List[List[int]]],
    config: Dict[str, Any],
    state: Dict[str, Any],
) -> GenerationResult:
    """Run specified generator or manage exhibition cycle across all modes."""
    active_mode = mode.lower().strip() if mode else "cycle"

    if active_mode in ("cycle", "auto", "exhibition"):
        # Cycle through modes
        last_cycled = state.get("last_cycled_mode", CYCLE_SEQUENCE[-1])
        try:
            next_idx = (CYCLE_SEQUENCE.index(last_cycled) + 1) % len(CYCLE_SEQUENCE)
            active_mode = CYCLE_SEQUENCE[next_idx]
        except (ValueError, IndexError):
            active_mode = CYCLE_SEQUENCE[0]
        state["last_cycled_mode"] = active_mode

    gen = get_generator(active_mode)
    if not gen:
        gen = AVAILABLE_GENERATORS["mondrian"]
        active_mode = "mondrian"

    result = gen.generate(previous_flagship, previous_note, config, state)
    result.metadata["active_mode"] = active_mode
    return result
