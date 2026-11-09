"""Unit tests for FirstComeSolver. Rings are passed in by hand, so these don't need the cycle finder."""

from __future__ import annotations

from conftest import load_fixture

from donorbridge.models import BloodGroup, Cycle, Family, Pool, Relation, Sex
from donorbridge.scoring import ExpectedTransplantScorer
from donorbridge.solvers.first_come import FirstComeSolver


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


def test_greedy_trap_takes_rings_in_arrival_order() -> None:
    # Arrival times (max id): (1,2) -> 2, (0,1,2) -> 2, (0,3) -> 3.
    # It takes (1,2), skips (0,1,2) because 1 and 2 are taken, then takes (0,3).
    solution = FirstComeSolver().solve(load_fixture("greedy_trap"), cycles=trap_rings())
    assert solution.cycles == (Cycle.of([0, 3]), Cycle.of([1, 2]))
    assert solution.transplants == 4


def test_ignores_weights() -> None:
    # (0,1) arrives before (0,1,2) in both cases, whatever the scorer says.
    pool = load_fixture("ring_vs_swap")
    for scorer in (None, ExpectedTransplantScorer(0.6), ExpectedTransplantScorer(0.9)):
        solution = FirstComeSolver(scorer=scorer).solve(pool, cycles=ring_vs_swap_rings())
        assert solution.cycles == (Cycle.of([0, 1]),)


def test_shorter_ring_wins_a_tie_in_arrival() -> None:
    # Both rings become possible when family 2 arrives; the shorter one goes first.
    pool = make_pool([0, 1, 2], [(0, 2), (2, 0), (0, 1), (1, 2)])
    rings = [Cycle.of([0, 1, 2]), Cycle.of([0, 2])]
    assert FirstComeSolver().solve(pool, cycles=rings).cycles == (Cycle.of([0, 2]),)


def test_ids_are_not_positions() -> None:
    pool = make_pool([40, 7, 1000], [(7, 40), (40, 7), (40, 1000), (1000, 7)])
    rings = [Cycle.of([7, 40]), Cycle.of([7, 40, 1000])]
    assert FirstComeSolver().solve(pool, cycles=rings).cycles == (Cycle.of([7, 40]),)


def test_empty_inputs() -> None:
    for name in ("empty", "no_edges"):
        assert FirstComeSolver().solve(load_fixture(name), cycles=[]).cycles == ()


def test_heuristic_flag_stats_and_repeatable() -> None:
    pool = load_fixture("greedy_trap")
    first = FirstComeSolver().solve(pool, cycles=trap_rings())
    second = FirstComeSolver().solve(pool, cycles=list(reversed(trap_rings())))
    assert first.optimal is False
    assert first.stats == {"rings_considered": 3, "rings_taken": 2}
    assert first.cycles == second.cycles  # input order doesn't matter


def test_does_not_change_the_input_list() -> None:
    rings = trap_rings()
    FirstComeSolver().solve(load_fixture("greedy_trap"), cycles=rings)
    assert rings == trap_rings()
