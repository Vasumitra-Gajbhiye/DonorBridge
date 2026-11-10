"""Unit tests for LocalSearchSolver. Rings come from a small helper here, not the cycle finder."""

from __future__ import annotations

import random

import pytest
from conftest import load_fixture

from donorbridge.models import BloodGroup, Cycle, Family, Pool, Relation, Sex
from donorbridge.scoring import CountScorer, ExpectedTransplantScorer, Scorer
from donorbridge.solvers.greedy import GreedySolver
from donorbridge.solvers.local_search import LocalSearchSolver, best_one_or_two


def make_pool(ids: list[int], edges: list[tuple[int, int]]) -> Pool:
    """A pool with dummy family details: the solvers only look at ids and edges."""
    families = tuple(
        Family(fid, BloodGroup.O, BloodGroup.O, Sex.F, Sex.M, Relation.OTHER, 0.1) for fid in ids
    )
    return Pool(families, frozenset(edges))


def all_rings(pool: Pool, max_len: int = 3) -> list[Cycle]:
    """Every ring of 2..max_len families, by plain search (independent of the cycle finder)."""
    succ = {fid: sorted(j for (i, j) in pool.edges if i == fid) for fid in pool.ids()}
    found: list[Cycle] = []

    def extend(start: int, path: list[int]) -> None:
        for nxt in succ[path[-1]]:
            if nxt == start and len(path) >= 2:
                found.append(Cycle.of(path))
            elif nxt > start and nxt not in path and len(path) < max_len:
                extend(start, path + [nxt])

    for start in pool.ids():
        extend(start, [start])
    return found


def random_pool(seed: int) -> Pool:
    """5–12 families with ids that are not 0..n-1, and random edges."""
    rng = random.Random(seed)
    ids = [3 + 7 * k for k in range(rng.randint(5, 12))]
    density = rng.choice((0.15, 0.25, 0.35))
    return make_pool(ids, [(i, j) for i in ids for j in ids if i != j and rng.random() < density])


def best_total(rings: list[Cycle], weight: dict[Cycle, float]) -> float:
    """The true optimum, by trying every set of disjoint rings (fine for tiny pools)."""

    def best(i: int, used: frozenset[int]) -> float:
        if i == len(rings):
            return 0.0
        skip = best(i + 1, used)
        if used.isdisjoint(rings[i].families):
            return max(skip, weight[rings[i]] + best(i + 1, used | set(rings[i].families)))
        return skip

    return best(0, frozenset())


def test_escapes_the_greedy_trap() -> None:
    # Greedy takes (0,1,2) = 3. Swapping it for (0,3) + (1,2) gains 1, so local search gets 4.
    solution = LocalSearchSolver().solve(load_fixture("greedy_trap"), cycles=all_rings(load_fixture("greedy_trap")))
    assert solution.cycles == (Cycle.of([0, 3]), Cycle.of([1, 2]))
    assert solution.transplants == 4
    assert solution.stats["moves"] == 1


def test_stuck_on_pool_8() -> None:
    # Reaching the optimum 7 needs BOTH 3-rings taken out at once; a 1-out move can't do it.
    pool = load_fixture("pool_8")
    solution = LocalSearchSolver().solve(pool, cycles=all_rings(pool))
    assert solution.transplants == 6
    assert solution.stats["moves"] == 0


def test_ring_vs_swap_follows_the_scorer() -> None:
    pool = load_fixture("ring_vs_swap")
    rings = all_rings(pool)
    assert LocalSearchSolver().solve(pool, cycles=rings).cycles == (Cycle.of([0, 1, 2]),)
    low_p = LocalSearchSolver(scorer=ExpectedTransplantScorer(0.6)).solve(pool, cycles=rings)
    high_p = LocalSearchSolver(scorer=ExpectedTransplantScorer(0.9)).solve(pool, cycles=rings)
    assert low_p.cycles == (Cycle.of([0, 1]),)
    assert high_p.cycles == (Cycle.of([0, 1, 2]),)


def test_between_greedy_and_the_optimum_on_random_pools() -> None:
    for seed in range(60):
        pool = random_pool(seed)
        rings = all_rings(pool)
        for scorer in (CountScorer(), ExpectedTransplantScorer(0.6), ExpectedTransplantScorer(0.9)):
            weight = {c: scorer.weight(c, pool) for c in rings}
            greedy = GreedySolver(scorer=scorer).solve(pool, cycles=rings).objective
            local = LocalSearchSolver(scorer=scorer).solve(pool, cycles=rings).objective
            assert greedy - 1e-9 <= local <= best_total(rings, weight) + 1e-9, (seed, scorer.name)


def test_best_one_or_two() -> None:
    a, b, c = Cycle.of([0, 1, 2]), Cycle.of([3, 4]), Cycle.of([0, 4])
    weight = {a: 3.0, b: 2.0, c: 2.0}
    assert best_one_or_two([a, b, c], weight) == (5.0, [a, b])  # a and b are disjoint
    assert best_one_or_two([a, c], weight) == (3.0, [a])  # a and c share family 0
    assert best_one_or_two([], weight) == (0.0, [])


def test_tiny_weights_still_improve() -> None:
    # A fixed 1e-9 threshold would ignore the gain of 1e-10 here; the scaled one doesn't.
    class TinyScorer(Scorer):
        name = "tiny"

        def weight(self, cycle: Cycle, pool: Pool) -> float:
            return 1e-10 * len(cycle)

    pool = load_fixture("greedy_trap")
    solution = LocalSearchSolver(scorer=TinyScorer()).solve(pool, cycles=all_rings(pool))
    assert solution.transplants == 4


def test_zero_time_limit_returns_a_valid_plan() -> None:
    pool = load_fixture("greedy_trap")
    solution = LocalSearchSolver(time_limit_s=0.0).solve(pool, cycles=all_rings(pool))
    assert solution.stats["timed_out"] is True
    assert solution.transplants >= 3  # at least greedy's plan; solve() has already validated it


def test_all_zero_weights() -> None:
    pool = load_fixture("greedy_trap")
    solution = LocalSearchSolver(scorer=ExpectedTransplantScorer(0.0)).solve(pool, cycles=all_rings(pool))
    assert solution.objective == pytest.approx(0.0)


def test_empty_inputs() -> None:
    for name in ("empty", "no_edges"):
        assert LocalSearchSolver().solve(load_fixture(name), cycles=[]).cycles == ()


def test_heuristic_flag_stats_and_repeatable() -> None:
    pool = load_fixture("pool_8")
    first = LocalSearchSolver().solve(pool, cycles=all_rings(pool))
    second = LocalSearchSolver().solve(pool, cycles=list(reversed(all_rings(pool))))
    assert first.optimal is False
    assert set(first.stats) == {"passes", "moves", "timed_out"}
    assert first.cycles == second.cycles
