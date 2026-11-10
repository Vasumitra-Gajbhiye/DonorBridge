"""Unit tests for BranchAndBoundSolver (versions 1, 2 and 3). Every test that checks an answer
compares it with brute force over all sets of disjoint rings."""

from __future__ import annotations

import random
import time

import pytest
from conftest import load_fixture

from donorbridge.models import BloodGroup, Cycle, Family, Pool, Relation, Sex
from donorbridge.scoring import CountScorer, ExpectedTransplantScorer, Scorer
from donorbridge.solvers.branch_bound import BranchAndBoundSolver

VERSIONS = (1, 2, 3)


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


def random_pool(seed: int, n_min: int = 5, n_max: int = 12) -> Pool:
    """Random edges among families whose ids are not 0..n-1."""
    rng = random.Random(seed)
    ids = [3 + 7 * k for k in range(rng.randint(n_min, n_max))]
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


class TableScorer(Scorer):
    """Any weights we like, to test beyond count and expected."""

    name = "table"

    def __init__(self, table: dict[Cycle, float]) -> None:
        self.table = table

    def weight(self, cycle: Cycle, pool: Pool) -> float:
        return self.table[cycle]


def solver(version: int, **kwargs: object) -> BranchAndBoundSolver:
    """A B&B solver running the given version."""
    bnb = BranchAndBoundSolver(**kwargs)
    bnb.version = version
    return bnb


@pytest.mark.parametrize("version", VERSIONS)
def test_fixtures(version: int) -> None:
    trap, pool_8, ring_vs_swap = (load_fixture(n) for n in ("greedy_trap", "pool_8", "ring_vs_swap"))
    solution = solver(version).solve(trap, cycles=all_rings(trap))
    assert solution.transplants == 4 and solution.optimal is True
    assert solver(version).solve(pool_8, cycles=all_rings(pool_8)).transplants == 7
    assert solver(version, max_cycle_len=2).solve(pool_8, cycles=all_rings(pool_8, 2)).transplants == 4
    rings = all_rings(ring_vs_swap)
    low_p = solver(version, scorer=ExpectedTransplantScorer(0.6)).solve(ring_vs_swap, cycles=rings)
    high_p = solver(version, scorer=ExpectedTransplantScorer(0.9)).solve(ring_vs_swap, cycles=rings)
    assert low_p.cycles == (Cycle.of([0, 1]),)
    assert high_p.cycles == (Cycle.of([0, 1, 2]),)


@pytest.mark.parametrize("version", VERSIONS)
def test_equals_brute_force_on_random_pools(version: int) -> None:
    for seed in range(40):
        pool = random_pool(seed)
        rings = all_rings(pool)
        rng = random.Random(seed)
        table = {c: rng.choice((0.0, 0.25, 1.0, 1.5, 2.0, 3.7)) for c in rings}
        for scorer in (CountScorer(), ExpectedTransplantScorer(0.6), ExpectedTransplantScorer(0.9), TableScorer(table)):
            weight = {c: scorer.weight(c, pool) for c in rings}
            solution = solver(version, scorer=scorer).solve(pool, cycles=rings)
            assert solution.optimal is True
            assert solution.objective == pytest.approx(best_total(rings, weight), abs=1e-9), (seed, scorer.name)


def test_v1_trace_on_the_trap() -> None:
    # The hand trace in docs/design/heuristics.md: 7 nodes, 2 prunes, starting from greedy's 3.
    trap = load_fixture("greedy_trap")
    stats = solver(1).solve(trap, cycles=all_rings(trap)).stats
    assert (stats["nodes"], stats["pruned"]) == (7, 2)


def test_v2_and_v3_search_fewer_nodes_than_v1() -> None:
    nodes = dict.fromkeys(VERSIONS, 0)
    for seed in range(15):
        pool = random_pool(seed, 10, 14)
        rings = all_rings(pool)
        for version in VERSIONS:
            nodes[version] += solver(version).solve(pool, cycles=rings).stats["nodes"]
    assert nodes[3] <= nodes[2] < nodes[1], nodes


@pytest.mark.parametrize("version", (2, 3))
def test_root_bound_is_never_below_the_optimum(version: int) -> None:
    for seed in range(30):
        pool = random_pool(seed)
        rings = all_rings(pool)
        weight = {c: len(c) * 0.7 ** len(c) for c in rings}
        stats = solver(version, scorer=ExpectedTransplantScorer(0.7)).solve(pool, cycles=rings).stats
        assert stats["root_bound"] >= best_total(rings, weight) - 1e-9, seed


@pytest.mark.parametrize("version", VERSIONS)
def test_tiny_weights_are_not_lost_to_the_tolerance(version: int) -> None:
    # With a fixed 1e-9 tolerance, 3e-10 was reported as optimal; the optimum is 4e-10.
    trap = load_fixture("greedy_trap")
    rings = all_rings(trap)
    tiny = TableScorer({c: 1e-10 * len(c) for c in rings})
    solution = solver(version, scorer=tiny).solve(trap, cycles=rings)
    assert solution.objective == pytest.approx(4e-10, rel=1e-6)
    assert solution.optimal is True


@pytest.mark.parametrize("version", VERSIONS)
def test_negative_weights_are_never_chosen(version: int) -> None:
    trap = load_fixture("greedy_trap")
    rings = [Cycle.of([0, 3]), Cycle.of([1, 2])]
    signed = TableScorer({rings[0]: 10.0, rings[1]: -20.0})
    solution = solver(version, scorer=signed).solve(trap, cycles=rings)
    assert solution.cycles == (Cycle.of([0, 3]),)
    assert solution.objective == pytest.approx(10.0)


@pytest.mark.parametrize("version", VERSIONS)
def test_all_zero_weights_and_empty_inputs(version: int) -> None:
    trap = load_fixture("greedy_trap")
    zero = solver(version, scorer=ExpectedTransplantScorer(0.0)).solve(trap, cycles=all_rings(trap))
    assert zero.objective == pytest.approx(0.0) and zero.optimal is True
    for name in ("empty", "no_edges"):
        solution = solver(version).solve(load_fixture(name), cycles=[])
        assert solution.cycles == () and solution.optimal is True


def test_zero_time_limit_returns_a_valid_plan() -> None:
    pool = load_fixture("pool_8")
    solution = solver(3, time_limit_s=0.0).solve(pool, cycles=all_rings(pool))
    assert solution.optimal is False
    assert solution.stats["timed_out"] is True
    assert solution.transplants >= 6  # at least the starting plan; solve() has already validated it


def test_stats_keys() -> None:
    pool = load_fixture("pool_8")
    stats = solver(3).solve(pool, cycles=all_rings(pool)).stats
    assert set(stats) == {"version", "nodes", "pruned", "timed_out", "time_to_best", "root_bound"}
    assert stats["version"] == 3 and stats["timed_out"] is False


@pytest.mark.slow
@pytest.mark.parametrize("version", VERSIONS)
def test_time_limit_on_a_big_pool(version: int) -> None:
    # The P3 integration check: n=200 with a 1 s limit gives a valid plan in under 1.5 s.
    # Random pools can be easy enough to finish, so `optimal` must simply match whether it timed out.
    rng = random.Random(0)
    ids = list(range(200))
    pool = make_pool(ids, [(i, j) for i in ids for j in ids if i != j and rng.random() < 0.15])
    rings = all_rings(pool)
    started = time.perf_counter()
    solution = solver(version, time_limit_s=1.0).solve(pool, cycles=rings)
    assert time.perf_counter() - started < 1.5
    assert solution.optimal is (not solution.stats["timed_out"])
