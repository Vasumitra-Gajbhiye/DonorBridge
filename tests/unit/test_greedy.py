"""Unit tests for GreedySolver. Rings are passed in by hand, so these don't need the cycle finder."""

from __future__ import annotations

import pytest
from conftest import load_fixture

from donorbridge.models import BloodGroup, Cycle, Family, Pool, Relation, Sex
from donorbridge.scoring import ExpectedTransplantScorer
from donorbridge.solvers.greedy import GreedySolver, conflict_counts


def make_pool(ids: list[int], edges: list[tuple[int, int]]) -> Pool:
    """A pool with dummy family details: the solvers only look at ids and edges."""
    families = tuple(
        Family(fid, BloodGroup.O, BloodGroup.O, Sex.F, Sex.M, Relation.OTHER, 0.1) for fid in ids
    )
    return Pool(families, frozenset(edges))


def trap_rings() -> list[Cycle]:
    """The three rings of the greedy_trap fixture.

    A function, not a module constant: building Cycles at import time would crash test
    collection while models.py is still a stub, instead of skipping like other tests.
    """
    return [Cycle.of([0, 3]), Cycle.of([1, 2]), Cycle.of([0, 1, 2])]


def ring_vs_swap_rings() -> list[Cycle]:
    """The two rings of the ring_vs_swap fixture."""
    return [Cycle.of([0, 1]), Cycle.of([0, 1, 2])]


def test_falls_into_the_greedy_trap() -> None:
    solution = GreedySolver().solve(load_fixture("greedy_trap"), cycles=trap_rings())
    assert solution.cycles == (Cycle.of([0, 1, 2]),)
    assert solution.transplants == 3  # the optimum, (0,3) + (1,2), is 4
    assert solution.objective == pytest.approx(3.0)


def test_ring_vs_swap_follows_the_scorer() -> None:
    pool = load_fixture("ring_vs_swap")
    count = GreedySolver().solve(pool, cycles=ring_vs_swap_rings())
    low_p = GreedySolver(scorer=ExpectedTransplantScorer(0.6)).solve(pool, cycles=ring_vs_swap_rings())
    high_p = GreedySolver(scorer=ExpectedTransplantScorer(0.9)).solve(pool, cycles=ring_vs_swap_rings())
    assert count.cycles == (Cycle.of([0, 1, 2]),)  # 3 > 2
    assert low_p.cycles == (Cycle.of([0, 1]),)  # 0.72 > 0.648
    assert high_p.cycles == (Cycle.of([0, 1, 2]),)  # 2.187 > 1.62


def test_conflict_counts() -> None:
    # (0,1,2) shares families with both others; (0,3) and (1,2) share nothing with each other.
    counts = conflict_counts(trap_rings())
    assert counts == {Cycle.of([0, 3]): 1, Cycle.of([1, 2]): 1, Cycle.of([0, 1, 2]): 2}


def test_neighbour_sharing_two_families_counts_once() -> None:
    rings = [Cycle.of([0, 1, 2]), Cycle.of([0, 2, 1])]  # same families, opposite direction
    assert conflict_counts(rings) == {rings[0]: 1, rings[1]: 1}


def test_ties_go_to_the_ring_with_fewest_conflicts() -> None:
    # Three swaps of equal weight in a row: 0-1, 1-2, 2-3. The middle one blocks both others,
    # so it has 2 conflicts and the outer two have 1. Greedy takes the outer two: 4 transplants.
    edges = [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2)]
    rings = [Cycle.of([1, 2]), Cycle.of([0, 1]), Cycle.of([2, 3])]
    solution = GreedySolver().solve(make_pool([0, 1, 2, 3], edges), cycles=rings)
    assert solution.cycles == (Cycle.of([0, 1]), Cycle.of([2, 3]))


def test_full_tie_goes_to_smallest_families() -> None:
    # Two swaps, same weight, same conflicts, sharing family 1: (0,1) beats (1,2).
    pool = make_pool([0, 1, 2], [(0, 1), (1, 0), (1, 2), (2, 1)])
    rings = [Cycle.of([1, 2]), Cycle.of([0, 1])]
    assert GreedySolver().solve(pool, cycles=rings).cycles == (Cycle.of([0, 1]),)


def test_empty_inputs() -> None:
    for name in ("empty", "no_edges"):
        assert GreedySolver().solve(load_fixture(name), cycles=[]).cycles == ()


def test_heuristic_flag_stats_and_repeatable() -> None:
    pool = load_fixture("greedy_trap")
    first = GreedySolver().solve(pool, cycles=trap_rings())
    second = GreedySolver().solve(pool, cycles=list(reversed(trap_rings())))
    assert first.optimal is False
    assert first.stats == {"rings_considered": 3, "rings_taken": 1}
    assert first.cycles == second.cycles and first.objective == second.objective
