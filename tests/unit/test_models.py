"""Unit tests for donorbridge.models: Family, Pool, Cycle, Solution."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from pathlib import Path

import pytest
from conftest import FIXTURES_DIR, load_fixture

from donorbridge.models import (
    BloodGroup,
    Cycle,
    Family,
    InvalidSolutionError,
    Pool,
    Relation,
    Sex,
    Solution,
)

ALL_FIXTURES = ("pool_8", "ring_vs_swap", "greedy_trap", "empty", "no_edges")

# The L=3 optimum of pool_8 (7 transplants), see report/01_lead/04_fixtures.md.
POOL_8_OPT_L3 = [(3, 12), (9, 14), (5, 7, 21)]


def make_family(fid: int, pra: float = 0.1) -> Family:
    """A family with dummy details; only the id (and sometimes PRA) matters here."""
    return Family(fid, BloodGroup.O, BloodGroup.A, Sex.F, Sex.M, Relation.OTHER, pra)


def make_pool(ids: Sequence[int], edges: Sequence[tuple[int, int]], name: str = "") -> Pool:
    """A pool of dummy families with the given ids (in the given order) and edges."""
    return Pool(tuple(make_family(fid) for fid in ids), frozenset(edges), name)


def make_solution(rings: Sequence[Sequence[int]]) -> Solution:
    """Wrap hand-picked rings in a Solution."""
    cycles = tuple(Cycle.of(ring) for ring in rings)
    return Solution(cycles, solver="hand", objective=0.0, runtime_s=0.0, optimal=None)


# ---------------------------------------------------------------- Family


def test_highly_sensitised_threshold_is_inclusive() -> None:
    assert not make_family(1, pra=0.79).highly_sensitised
    assert make_family(1, pra=0.80).highly_sensitised  # pool_8 family 21 sits exactly here
    assert make_family(1, pra=1.0).highly_sensitised


# ---------------------------------------------------------------- Pool construction


def test_pool_rejects_duplicate_ids() -> None:
    with pytest.raises(ValueError, match="duplicate family id 7"):
        make_pool([7, 3, 7], [])


def test_pool_rejects_self_loop() -> None:
    with pytest.raises(ValueError, match=r"edge \(3, 3\) is a self-loop"):
        make_pool([3, 5], [(3, 3)])


def test_pool_rejects_edge_to_unknown_id() -> None:
    with pytest.raises(ValueError, match="family id 99"):
        make_pool([3, 5], [(3, 5), (5, 99)])


def test_ids_are_sorted_and_not_positions() -> None:
    pool = make_pool([40, 7, 1000], [(7, 40), (40, 1000)])
    assert pool.n == 3
    assert pool.ids() == (7, 40, 1000)
    assert pool.family(1000).id == 1000
    assert pool.family(7) is pool.families[1]


def test_family_lookup_missing_id_raises_key_error() -> None:
    pool = make_pool([40, 7], [])
    with pytest.raises(KeyError, match="no family with id 0"):
        pool.family(0)


# ---------------------------------------------------------------- JSON


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_json_round_trip_dict(name: str) -> None:
    pool = load_fixture(name)
    assert Pool.from_dict(pool.to_dict()) == pool
    as_text = json.dumps(pool.to_dict())  # must be JSON-ready: enums written as plain strings
    assert Pool.from_dict(json.loads(as_text)) == pool


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_json_round_trip_file(name: str, tmp_path: Path) -> None:
    pool = load_fixture(name)
    path = tmp_path / f"{name}.json"
    pool.save_json(path)
    assert Pool.load_json(path) == pool
    assert Pool.load_json(str(path)) == pool  # str paths work too


def test_to_dict_matches_fixture_file() -> None:
    """to_dict uses the same format as the hand-written fixture: enum values, edges sorted."""
    on_disk = json.loads((FIXTURES_DIR / "pool_8.json").read_text(encoding="utf-8"))
    as_dict = load_fixture("pool_8").to_dict()
    assert as_dict == on_disk
    assert as_dict["edges"] == sorted(as_dict["edges"])
    assert as_dict["families"][0]["patient_blood"] == "O"
    assert as_dict["families"][0]["relation"] == "spouse"


def test_from_dict_ignores_unknown_top_level_keys() -> None:
    d = load_fixture("ring_vs_swap").to_dict()
    d["comment"] = "extra keys are fine"
    assert Pool.from_dict(d) == load_fixture("ring_vs_swap")


# ---------------------------------------------------------------- subpool / without_edges


def test_subpool_is_induced_and_does_not_mutate() -> None:
    pool = load_fixture("pool_8")
    before = pool.to_dict()
    sub = pool.subpool([3, 12, 7], name="trio")
    assert sub.ids() == (3, 7, 12)
    assert sub.edges == frozenset({(3, 12), (12, 3), (12, 7), (7, 3)})
    assert sub.name == "trio"
    assert pool.to_dict() == before


def test_subpool_of_every_id_keeps_all_edges() -> None:
    pool = load_fixture("pool_8")
    assert pool.subpool(pool.ids(), name=pool.name) == pool


def test_subpool_rejects_unknown_ids() -> None:
    with pytest.raises(ValueError, match=re.escape("[99]")):
        load_fixture("pool_8").subpool([3, 99])


def test_without_edges_removes_only_those_and_does_not_mutate() -> None:
    pool = load_fixture("pool_8")
    smaller = pool.without_edges([(3, 12), (14, 9), (1, 21)])  # (1, 21) is not an edge: ignored
    assert smaller.edges == pool.edges - {(3, 12), (14, 9)}
    assert smaller.families == pool.families
    assert smaller.name == pool.name
    assert (3, 12) in pool.edges  # original untouched


# ---------------------------------------------------------------- Cycle


def test_cycle_canonical_rotation_keeps_direction() -> None:
    assert Cycle.of([3, 1, 2]) == Cycle.of([1, 2, 3]) == Cycle.of([2, 3, 1])
    assert Cycle.of([2, 3, 1]).families == (1, 2, 3)
    assert Cycle.of([3, 1, 2]) != Cycle.of([1, 3, 2])  # opposite direction: a different ring
    assert Cycle.of((21, 5, 7)).families == (5, 7, 21)


def test_cycle_edges_and_len() -> None:
    ring = Cycle.of([12, 7, 3])
    assert ring.families == (3, 12, 7)
    assert ring.edges() == ((3, 12), (12, 7), (7, 3))
    assert len(ring) == 3
    assert Cycle.of([9, 14]).edges() == ((9, 14), (14, 9))


def test_cycle_is_hashable() -> None:
    weights = {Cycle.of([2, 1]): 2.0}
    assert weights[Cycle.of([1, 2])] == 2.0


@pytest.mark.parametrize("seq", [[], [4], [1, 2, 1], [5, 6, 6]])
def test_cycle_of_rejects_short_or_repeated(seq: list[int]) -> None:
    with pytest.raises(ValueError):
        Cycle.of(seq)


def test_cycle_constructor_rejects_non_canonical() -> None:
    with pytest.raises(ValueError, match="canonical"):
        Cycle((2, 1))
    assert Cycle((1, 2)).families == (1, 2)


# ---------------------------------------------------------------- Solution


def test_solution_transplants_and_covered() -> None:
    plan = make_solution(POOL_8_OPT_L3)
    assert plan.transplants == 7
    assert plan.covered() == frozenset({3, 12, 9, 14, 5, 7, 21})


def test_validate_accepts_a_valid_plan() -> None:
    make_solution(POOL_8_OPT_L3).validate(load_fixture("pool_8"), max_cycle_len=3)


def test_validate_rejects_overlap() -> None:
    plan = make_solution([(3, 12), (3, 12, 7)])
    with pytest.raises(InvalidSolutionError, match="family 3 is in two rings"):
        plan.validate(load_fixture("pool_8"), max_cycle_len=3)


def test_validate_rejects_missing_edge() -> None:
    plan = make_solution([(1, 3)])  # 1 -> 3 exists, 3 -> 1 does not
    with pytest.raises(InvalidSolutionError, match=re.escape("ring (1, 3) needs edge 3 -> 1")):
        plan.validate(load_fixture("pool_8"), max_cycle_len=3)


def test_validate_rejects_too_long() -> None:
    plan = make_solution([(3, 12, 7)])
    with pytest.raises(InvalidSolutionError, match=re.escape("ring (3, 12, 7) has 3 families")):
        plan.validate(load_fixture("pool_8"), max_cycle_len=2)


def test_validate_rejects_unknown_id() -> None:
    plan = make_solution([(3, 99)])
    with pytest.raises(InvalidSolutionError, match="uses family 99"):
        plan.validate(load_fixture("pool_8"), max_cycle_len=3)


def test_validate_rejects_too_short() -> None:
    # Cycle refuses to build a 1-family ring, so this check is defensive. Bypass __post_init__
    # to prove validate still catches one.
    lonely = object.__new__(Cycle)
    object.__setattr__(lonely, "families", (3,))
    plan = Solution((lonely,), solver="hand", objective=0.0, runtime_s=0.0, optimal=None)
    with pytest.raises(InvalidSolutionError, match=re.escape("ring (3,) has 1 families")):
        plan.validate(load_fixture("pool_8"), max_cycle_len=3)


def test_invalid_solution_error_is_a_value_error() -> None:
    assert issubclass(InvalidSolutionError, ValueError)


def test_solution_equality_ignores_stats() -> None:
    a = Solution((Cycle.of([1, 2]),), "x", 2.0, 0.1, True, stats={"nodes": 5})
    b = Solution((Cycle.of([1, 2]),), "x", 2.0, 0.1, True, stats={"nodes": 9})
    assert a == b


# ---------------------------------------------------------------- empty pool


def test_empty_pool() -> None:
    pool = load_fixture("empty")
    assert pool.n == 0
    assert pool.ids() == ()
    assert pool == Pool((), frozenset(), "empty")
    assert Pool.from_dict(pool.to_dict()) == pool
    assert pool.subpool([]) == Pool((), frozenset())
    assert pool.without_edges([]) == pool

    nothing = make_solution([])
    nothing.validate(pool, max_cycle_len=3)
    assert nothing.transplants == 0
    assert nothing.covered() == frozenset()
