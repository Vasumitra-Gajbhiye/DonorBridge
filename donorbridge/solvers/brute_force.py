"""Brute force: try every set of disjoint rings (tiny pools only; the test oracle).

Owner: Matching
Implemented in: P2
"""

from __future__ import annotations

from typing import ClassVar

from donorbridge.models import Cycle, Pool
from donorbridge.solvers.base import Solver


class BruteForceSolver(Solver):
    """Enumerate every vertex-disjoint subset of rings and keep the heaviest. Exponential: for n <= 12."""

    name: ClassVar[str] = "brute-force"
    exact: ClassVar[bool] = True
    supported_lengths: ClassVar[tuple[int, ...]] = (2, 3, 4)

    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """See the class docstring. Returns (chosen rings, optimal flag, stats)."""
        raise NotImplementedError("Matching, P2")
