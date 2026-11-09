"""Greedy heuristic: heaviest disjoint rings first.

Owner: Heuristics
Implemented in: P1
"""

from __future__ import annotations

from collections import defaultdict
from typing import ClassVar

from donorbridge.models import Cycle, Pool
from donorbridge.solvers.base import Solver


def conflict_counts(cycles: list[Cycle]) -> dict[Cycle, int]:
    """For each ring, how many OTHER rings share at least one family with it."""
    # family id -> positions (in `cycles`) of the rings that contain it.
    # Positions, not Cycle objects: ints are much faster to hash, and a pool of 200
    # has over 20,000 rings.
    rings_with: dict[int, set[int]] = defaultdict(set)
    for position, ring in enumerate(cycles):
        for fam in ring.families:
            rings_with[fam].add(position)

    counts: dict[Cycle, int] = {}
    for ring in cycles:
        # A set union, so a ring that shares two families with this one counts once.
        touching = set().union(*(rings_with[fam] for fam in ring.families))
        counts[ring] = len(touching) - 1  # minus the ring itself
    return counts


class GreedySolver(Solver):
    """Sort rings by weight (descending), ties by fewest conflicting rings, then by families;
    take each ring disjoint from those already taken."""

    name: ClassVar[str] = "greedy"
    exact: ClassVar[bool] = False
    supported_lengths: ClassVar[tuple[int, ...]] = (2, 3, 4)

    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """See the class docstring. Returns (chosen rings, optimal flag, stats)."""
        weight = self.weights(pool, cycles)  # never len(c): this is what makes greedy failure-aware
        conflicts = conflict_counts(cycles)
        best_first = sorted(cycles, key=lambda c: (-weight[c], conflicts[c], c.families))

        chosen: list[Cycle] = []
        covered: set[int] = set()
        for ring in best_first:
            if covered.isdisjoint(ring.families):
                chosen.append(ring)
                covered.update(ring.families)

        stats = {"rings_considered": len(cycles), "rings_taken": len(chosen)}
        return chosen, False, stats
