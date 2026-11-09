"""Solver base class: the template method every solver plugs into.

Owner: Lead
Implemented in: P1
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import ClassVar

from donorbridge.models import Cycle, Pool, Solution
from donorbridge.scoring import CountScorer, Scorer


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
        if max_cycle_len not in self.supported_lengths:
            raise ValueError(
                f"{self.name} supports max_cycle_len in {self.supported_lengths}, got {max_cycle_len}"
            )
        self.max_cycle_len = max_cycle_len
        self.scorer: Scorer = scorer if scorer is not None else CountScorer()
        self.time_limit_s = time_limit_s
        self.seed = seed  # randomised subclasses build random.Random(self.seed); no global state

    def solve(self, pool: Pool, cycles: list[Cycle] | None = None) -> Solution:
        """Template method: find rings if None, drop rings longer than max_cycle_len, time _solve(),
        score with self.scorer, build the Solution (optimal forced False if not exact), validate, return."""
        # 1. Find the rings ourselves only if the caller did not pass them in.
        #    Imported here, not at the top, as the L1.4 spec asks.
        if cycles is None:
            from donorbridge.cycles import find_cycles

            cycles = find_cycles(pool, self.max_cycle_len)

        # 2. Keep only rings this solver may use. Builds a new list, so the caller's list is untouched.
        cycles = [c for c in cycles if len(c) <= self.max_cycle_len]

        # 3. The one step each subclass supplies, timed on its own (ring enumeration is not included).
        t0 = time.perf_counter()
        chosen, optimal, stats = self._solve(pool, cycles)
        runtime = time.perf_counter() - t0

        # 4. A heuristic can never claim to have proven optimality.
        if not self.exact:
            optimal = False

        # 5. Build the Solution: rings in a fixed order, objective from this solver's scorer.
        solution = Solution(
            tuple(sorted(chosen, key=lambda c: (len(c), c.families))),
            self.name,
            self.scorer.total(chosen, pool),
            runtime,
            optimal,
            stats,
        )

        # 6. Never hand back an invalid plan: raises InvalidSolutionError if _solve made a mistake.
        solution.validate(pool, self.max_cycle_len)
        return solution

    def weights(self, pool: Pool, cycles: list[Cycle]) -> dict[Cycle, float]:
        """Scorer weight per ring. Subclasses compare rings with these, never with len(c)."""
        return {c: self.scorer.weight(c, pool) for c in cycles}

    def __repr__(self) -> str:
        """For example: GreedySolver(name='greedy', max_cycle_len=3, scorer='count')."""
        return (
            f"{type(self).__name__}(name={self.name!r}, max_cycle_len={self.max_cycle_len}, "
            f"scorer={self.scorer.name!r})"
        )

    @abstractmethod
    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """Return (chosen rings, optimal flag, stats dict). Rings are already filtered by length."""
