"""Branch and bound: exact search over include/exclude decisions with a weight bound.

Owner: Heuristics
Implemented in: P2
"""

from __future__ import annotations

import math
import time
from typing import ClassVar

from donorbridge.models import Cycle, Pool
from donorbridge.solvers.base import Solver
from donorbridge.solvers.greedy import GreedySolver
from donorbridge.solvers.local_search import LocalSearchSolver

RELATIVE_TOLERANCE = 1e-9  # "better" means better by more than this fraction of the heaviest ring
CHECK_CLOCK_EVERY = 64  # reading the clock costs far less than a node, but no need at every node
ROOT_STEPS = 100  # version 3: toll steps at the root, where a tight bound pays off most
NODE_STEPS = 10  # version 3: toll steps at every other node (it starts from its parent's tolls)


class _OutOfTime(Exception):
    """Unwinds the whole search at once. The best solution is already saved as a copy."""


class BranchAndBoundSolver(Solver):
    """Include/exclude branching over rings with an upper bound for pruning; honours time_limit_s
    (optimal=False on timeout). stats: nodes, pruned, timed_out.

    version 1: branch on rings, bound = value + weight of every remaining ring that still fits.
    version 2: branch on the most constrained family, bound = value + each undecided family's
    best share w(c)/|c| (the playbook's bound).
    version 3 (default): version 2 plus a toll (Lagrangian) bound, rounded down when every weight
    is a whole number. Set `solver.version = 1` or `2` to compare.
    """

    name: ClassVar[str] = "branch-bound"
    exact: ClassVar[bool] = True
    supported_lengths: ClassVar[tuple[int, ...]] = (2, 3, 4)
    version: ClassVar[int] = 3

    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """See the class docstring. Returns (chosen rings, optimal flag, stats)."""
        # ONE deadline for everything, including building the starting solution below.
        self._started = time.perf_counter()
        self._deadline = None if self.time_limit_s is None else self._started + self.time_limit_s
        self._nodes = self._pruned = 0
        self._time_to_best = 0.0

        # The bounds below assume weights >= 0. A ring with negative weight can never be in an
        # optimal plan (dropping it raises the total), so leaving such rings out keeps B&B exact.
        weight_of = self.weights(pool, cycles)
        cycles = [c for c in cycles if weight_of[c] >= 0]

        # Number the rings 0..R-1 and keep plain lists: the search touches these millions of times,
        # and list[int] is much faster than hashing Cycle objects. These are ring positions, not
        # family ids, so the "ids are not indices" rule still holds.
        self._rings = cycles
        self._members = [c.families for c in cycles]
        self._w = [weight_of[c] for c in cycles]
        # A fixed 1e-9 would swallow real differences when weights are tiny, so the tolerance is
        # scaled to the heaviest ring (it is 0 when every weight is 0).
        self._tolerance = RELATIVE_TOLERANCE * max(self._w, default=0.0)
        # With whole-number weights (the count scorer) every plan's total is a whole number, so a
        # bound of 23.4 really means "at most 23". Version 3 rounds its bound down in that case.
        self._whole_weights = all(float(x).is_integer() for x in self._w)

        # Incumbent: the best complete solution so far. v1 starts from greedy, v2 from local search,
        # which gets only the time that is left.
        if self.version == 1:
            first = GreedySolver(self.max_cycle_len, self.scorer)._solve(pool, cycles)[0]
        else:
            remaining = None if self._deadline is None else max(0.0, self._deadline - time.perf_counter())
            first = LocalSearchSolver(self.max_cycle_len, self.scorer, remaining)._solve(pool, cycles)[0]
        self._best = list(first)
        self._best_value = sum(weight_of[c] for c in first)

        stats: dict = {"version": self.version}
        timed_out = False
        try:
            if self._deadline is not None and time.perf_counter() > self._deadline:
                raise _OutOfTime  # the starting solution used up the whole budget
            if self.version == 1:
                self._search_rings()
            else:
                self._search_families(stats)
        except _OutOfTime:
            timed_out = True

        stats.update(nodes=self._nodes, pruned=self._pruned, timed_out=timed_out,
                     time_to_best=self._time_to_best)
        return self._best, not timed_out, stats

    def _tick(self) -> None:
        """Count one node, and every CHECK_CLOCK_EVERY nodes stop if time is up."""
        self._nodes += 1
        if (
            self._deadline is not None
            and self._nodes % CHECK_CLOCK_EVERY == 0
            and time.perf_counter() > self._deadline
        ):
            raise _OutOfTime

    def _record(self, chosen: list[int], value: float) -> None:
        """Save `chosen` as the new incumbent if it is better. Copies it: `chosen` keeps changing."""
        if value > self._best_value + self._tolerance:
            self._best = [self._rings[r] for r in chosen]
            self._best_value = value
            self._time_to_best = time.perf_counter() - self._started

    # ---------------- version 1: include or exclude each ring ----------------

    def _search_rings(self) -> None:
        w, members = self._w, self._members
        order = sorted(range(len(w)), key=lambda r: (-w[r], members[r]))
        chosen: list[int] = []
        covered: set[int] = set()

        def explore(i: int, value: float) -> None:
            # "Exclude ring i" is the `i += 1` at the bottom of the loop, not a recursive call.
            # A pool of 100 has thousands of rings; one call per ring would pass Python's
            # recursion limit (1,000). This way the depth is at most the number of chosen rings.
            self._tick()
            while i < len(order):
                bound = value + sum(w[r] for r in order[i:] if covered.isdisjoint(members[r]))
                if bound <= self._best_value + self._tolerance:
                    self._pruned += 1
                    return
                ring = order[i]
                if covered.isdisjoint(members[ring]):  # branch 1: include ring i
                    chosen.append(ring)
                    covered.update(members[ring])
                    self._record(chosen, value + w[ring])
                    explore(i + 1, value + w[ring])
                    chosen.pop()
                    covered.difference_update(members[ring])
                self._tick()
                i += 1  # branch 2: exclude ring i

        explore(0, 0.0)

    # ---------------- version 2: decide one family at a time ----------------

    def _search_families(self, stats: dict) -> None:
        w, members = self._w, self._members
        rings_of: dict[int, list[int]] = {}
        for r, fams in enumerate(members):
            for fam in fams:
                rings_of.setdefault(fam, []).append(r)
        families = sorted(rings_of)  # a family in no ring can never add anything

        # The same rings in two orders: heaviest first to branch, biggest share first for the bound.
        for fam in families:
            rings_of[fam].sort(key=lambda r: (-w[r], members[r]))
        by_share = {fam: sorted(rings_of[fam], key=lambda r: -w[r] / len(members[r])) for fam in families}

        # blocks[r]     = how many of ring r's families are decided. Ring r is available when it is 0.
        # available[u]  = how many available rings contain family u. 0 means u needs no decision.
        blocks = [0] * len(w)
        available = {fam: len(rings_of[fam]) for fam in families}
        chosen: list[int] = []

        def decide(fam: int) -> None:
            for r in rings_of[fam]:
                blocks[r] += 1
                if blocks[r] == 1:  # ring r just stopped being available
                    for member in members[r]:
                        available[member] -= 1

        def undo(fam: int) -> None:
            for r in rings_of[fam]:
                blocks[r] -= 1
                if blocks[r] == 0:  # ring r is available again
                    for member in members[r]:
                        available[member] += 1

        def bound_and_branch_family(value: float) -> tuple[float, int | None]:
            """Upper bound for this node, and the family with the fewest available rings (ties:
            smallest id). The family is None when nothing is left to decide."""
            bound, branch_on, fewest = value, None, len(w) + 1
            for fam in families:
                if available[fam] == 0:
                    continue
                best_ring = next(r for r in by_share[fam] if blocks[r] == 0)
                bound += w[best_ring] / len(members[best_ring])
                if available[fam] < fewest:
                    branch_on, fewest = fam, available[fam]
            return bound, branch_on

        # Version 3: one toll per family. Kept between nodes, so each node starts from the tolls
        # its parent left behind (any tolls >= 0 give a valid bound, so this is always safe).
        # Starting tolls = each family's best share, which makes the first bound equal v2's.
        toll = {fam: w[by_share[fam][0]] / len(members[by_share[fam][0]]) for fam in families}

        def toll_bound(value: float, steps: int) -> float:
            """Version 3's bound (Lagrangian relaxation): tolls + every positive ring profit.

            Each family u pays a toll >= 0; a ring's profit is its weight minus its families' tolls.
            For any set of disjoint rings, weight = profit + tolls of its own families, and each
            family is in at most one ring, so the set is worth at most
                sum of all tolls + sum of the positive profits.
            That holds for ANY tolls, so we can lower the bound freely: each step moves a toll
            down where no profitable ring uses its family, and up where several do.
            """
            active = [fam for fam in families if available[fam] > 0]
            open_rings = [r for r in range(len(w)) if blocks[r] == 0]
            target = self._best_value + self._tolerance - value  # reaching this means we can prune
            best = math.inf
            for _ in range(steps):
                if self._deadline is not None and time.perf_counter() > self._deadline:
                    raise _OutOfTime
                total = sum(toll[fam] for fam in active)
                used_by = dict.fromkeys(active, 0)  # how many profitable rings use each family
                for r in open_rings:
                    profit = w[r] - sum(toll[m] for m in members[r])
                    if profit > 0:
                        total += profit
                        for m in members[r]:
                            used_by[m] += 1
                best = min(best, total)
                if best <= target:
                    break  # good enough to prune this node
                slope = {fam: 1 - used_by[fam] for fam in active}
                norm = sum(g * g for g in slope.values())
                if norm == 0:
                    break  # every family is used exactly once: these tolls can't be improved
                step = (total - target) / norm  # Polyak step: aim straight at the prune target
                for fam in active:
                    toll[fam] = max(0.0, toll[fam] - step * slope[fam])
            return value + best

        def explore(value: float) -> None:
            self._tick()
            bound, fam = bound_and_branch_family(value)
            if self.version == 3 and fam is not None and bound > self._best_value + self._tolerance:
                bound = min(bound, toll_bound(value, NODE_STEPS))  # only if v2's bound didn't prune
            if fam is None:
                return  # leaf: no ring is available any more
            if self.version == 3 and self._whole_weights:
                bound = math.floor(bound + self._tolerance)
            if bound <= self._best_value + self._tolerance:
                self._pruned += 1
                return

            for r in list(rings_of[fam]):  # children 1..k: fam goes into ring r, heaviest first
                if blocks[r] != 0:
                    continue
                chosen.append(r)
                for member in members[r]:
                    decide(member)
                self._record(chosen, value + w[r])
                explore(value + w[r])
                for member in members[r]:
                    undo(member)
                chosen.pop()

            decide(fam)  # last child: fam stays unmatched
            explore(value)
            undo(fam)

        root_bound = bound_and_branch_family(0.0)[0]
        if self.version == 3 and families:
            root_bound = min(root_bound, toll_bound(0.0, ROOT_STEPS))
        stats["root_bound"] = root_bound
        explore(0.0)
