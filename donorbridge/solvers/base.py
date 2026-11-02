"""Solver base class: the template method every solver plugs into.

Owner: Lead
Implemented in: P1
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from donorbridge.models import Cycle, Pool, Solution
from donorbridge.scoring import Scorer


class Solver(ABC):
    """Chooses vertex-disjoint rings that maximise total scorer weight.

    Subclasses set the ClassVars and implement only `_solve`; `solve` does everything else.
    """

    name: ClassVar[str]
    exact: ClassVar[bool]
    supported_lengths: ClassVar[tuple[int, ...]] = (2, 3, 4)

    def __init__(
        self,
        max_cycle_len: int = 3,
        scorer: Scorer | None = None,
        time_limit_s: float | None = None,
        seed: int = 0,
    ) -> None:
        """Store settings. ValueError if max_cycle_len not in supported_lengths.
        scorer defaults to CountScorer()."""
        raise NotImplementedError("Lead, P1")

    def solve(self, pool: Pool, cycles: list[Cycle] | None = None) -> Solution:
        """Template method: find rings if None, drop rings longer than max_cycle_len, time _solve(),
        score with self.scorer, build the Solution (optimal forced False if not exact), validate, return."""
        raise NotImplementedError("Lead, P1")

    def weights(self, pool: Pool, cycles: list[Cycle]) -> dict[Cycle, float]:
        """Scorer weight per ring. Subclasses compare rings with these, never with len(c)."""
        raise NotImplementedError("Lead, P1")

    @abstractmethod
    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """Return (chosen rings, optimal flag, stats dict). Rings are already filtered by length."""
