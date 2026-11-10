"""Local search: improve a greedy start by swapping one ring out for up to two rings in.

Owner: Heuristics
Implemented in: P2
"""

from __future__ import annotations

import time
from typing import ClassVar

from donorbridge.models import Cycle, Pool
from donorbridge.solvers.base import Solver
from donorbridge.solvers.greedy import GreedySolver

RELATIVE_TOLERANCE = 1e-9  # a move must gain more than this fraction of the heaviest ring


def best_one_or_two(candidates: list[Cycle], weight: dict[Cycle, float]) -> tuple[float, list[Cycle]]:
    """The heaviest set of at most 2 disjoint rings. `candidates` must be sorted heaviest first."""
    best_value, best_set = 0.0, []
    for i, first in enumerate(candidates):
        if weight[first] > best_value:
            best_value, best_set = weight[first], [first]
        # Later rings are lighter, so once two copies of `first` can't win, nothing after it can.
        if 2 * weight[first] <= best_value:
            break
        for second in candidates[i + 1 :]:
            value = weight[first] + weight[second]
            if value <= best_value:
                break  # sorted heaviest first: every later `second` is lighter still
            if set(first.families).isdisjoint(second.families):
                best_value, best_set = value, [first, second]
    return best_value, best_set


class LocalSearchSolver(Solver):
    """Start from greedy; repeatedly replace one chosen ring with the best set of at most two disjoint
    rings using its families plus uncovered ones, while total weight improves."""

    name: ClassVar[str] = "local-search"
    exact: ClassVar[bool] = False
    supported_lengths: ClassVar[tuple[int, ...]] = (2, 3, 4)

    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """See the class docstring. Returns (chosen rings, optimal flag, stats)."""
        deadline = None if self.time_limit_s is None else time.perf_counter() + self.time_limit_s
        weight = self.weights(pool, cycles)
        heaviest_first = sorted(cycles, key=lambda c: (-weight[c], c.families))
        # Scaled, not a fixed 1e-9: with tiny weights a fixed value would hide real improvements.
        # Every applied move still gains more than this, so the search always stops.
        self._tolerance = RELATIVE_TOLERANCE * max(weight.values(), default=0.0)
        greedy = GreedySolver(self.max_cycle_len, self.scorer)
        chosen = greedy._solve(pool, cycles)[0]

        passes = moves = 0
        timed_out = False
        while True:
            passes += 1
            ring_out, rings_in, timed_out = self._best_move(chosen, heaviest_first, weight, deadline)
            if not rings_in:
                break
            if ring_out is not None:
                chosen.remove(ring_out)
            chosen.extend(rings_in)
            moves += 1
            if timed_out:
                break

        return chosen, False, {"passes": passes, "moves": moves, "timed_out": timed_out}

    def _best_move(
        self,
        chosen: list[Cycle],
        heaviest_first: list[Cycle],
        weight: dict[Cycle, float],
        deadline: float | None,
    ) -> tuple[Cycle | None, list[Cycle], bool]:
        """Look at every move once. Returns (ring taken out, rings put in, timed out).
        `rings_in` is empty when no move improves the total."""
        owner = {fam: ring for ring in chosen for fam in ring.families}

        # Sort every ring by which chosen rings block it. A ring blocked by two or more
        # chosen rings can't be used by a move that removes only one, so it is dropped here.
        free_rings: list[Cycle] = []
        blocked_only_by: dict[Cycle, list[Cycle]] = {ring: [] for ring in chosen}
        for ring in heaviest_first:  # so both lists stay sorted heaviest first
            blockers = {owner[fam] for fam in ring.families if fam in owner}
            if not blockers:
                free_rings.append(ring)
            elif len(blockers) == 1:
                blocker = blockers.pop()
                if ring != blocker:
                    blocked_only_by[blocker].append(ring)

        gain, ring_out, rings_in = 0.0, None, []

        # Add move. Greedy leaves no free ring, but after a swap there can be one.
        if free_rings and weight[free_rings[0]] > 0:
            gain, rings_in = weight[free_rings[0]], [free_rings[0]]

        # Swap moves, in a fixed order so every run gives the same answer.
        for ring in sorted(chosen, key=lambda c: c.families):
            if deadline is not None and time.perf_counter() > deadline:
                return ring_out, rings_in, True
            candidates = sorted(blocked_only_by[ring] + free_rings, key=lambda c: (-weight[c], c.families))
            value, replacement = best_one_or_two(candidates, weight)
            swap_gain = value - weight[ring]
            if swap_gain > self._tolerance and swap_gain > gain:
                gain, ring_out, rings_in = swap_gain, ring, replacement

        return ring_out, rings_in, False
