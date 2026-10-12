"""Base abstractions for Kinetic Canvas visual generators."""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GenerationResult:
    """The generated artwork matrices and descriptive metadata."""
    flagship_matrix: List[List[int]]  # 6 rows x 22 cols of Vestaboard character codes
    note_matrix: List[List[int]]      # 3 rows x 15 cols of Vestaboard character codes
    title: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class GeneratorBase(ABC):
    """Abstract base class for all procedural / generative split-flap canvas artists."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Machine identifier of the generator."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human readable title of this generative style."""
        pass

    @abstractmethod
    def generate(
        self,
        previous_flagship: Optional[List[List[int]]],
        previous_note: Optional[List[List[int]]],
        config: Dict[str, Any],
        state: Dict[str, Any],
    ) -> GenerationResult:
        """Generate the next composition for both Flagship (22x6) and Note (15x3) displays."""
        pass
