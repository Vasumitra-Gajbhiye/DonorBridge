"""Unit tests for donorbridge.solvers.base (the Solver template method) and the solver registry."""

from __future__ import annotations

from typing import ClassVar

import pytest
from conftest import load_fixture

import donorbridge.cycles
from donorbridge.models import Cycle, InvalidSolutionError, Pool
from donorbridge.scoring import CountScorer, ExpectedTransplantScorer
from donorbridge.solvers import SOLVERS, GreedySolver, Solver, get_solver

# ring_vs_swap: families 0, 1, 2; edges 0->1, 1->0, 1->2, 2->0.
# Its two rings share families 0 and 1, so a plan can use only one of them.
SWAP = Cycle.of([0, 1])
RING = Cycle.of([0, 1, 2])

# greedy_trap: rings (0, 3), (1, 2) and (0, 1, 2).
TRAP_A = Cycle.of([0, 3])
TRAP_B = Cycle.of([1, 2])
TRAP_RING = Cycle.of([0, 1, 2])


# ----------------------------------------------------------------------------- test doubles


class DummySolver(Solver):
    """Test-only exact solver: takes rings first-fit in the order given, skipping any that overlap."""

    name: ClassVar[str] = "dummy"
    exact: ClassVar[bool] = True

    def __init__(self, *args, **kwargs) -> None:
        """Same arguments as Solver; also remembers the rings _solve was given."""
        super().__init__(*args, **kwargs)
        self.seen: list[Cycle] | None = None

    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """First-fit disjoint rings; claims optimality."""
        self.seen = list(cycles)
        used: set[int] = set()
        chosen: list[Cycle] = []
        for cycle in cycles:
            if used.isdisjoint(cycle.families):
                chosen.append(cycle)
                used.update(cycle.families)
        return chosen, True, {"seen": len(cycles)}


class HeuristicDummy(DummySolver):
    """Same as DummySolver, but not exact: its optimal=True must be overridden to False."""

    name: ClassVar[str] = "heuristic-dummy"
    exact: ClassVar[bool] = False


class ReturnsDummy(Solver):
    """Test-only solver that ignores the rings and returns a fixed answer (to feed bad plans in)."""

    name: ClassVar[str] = "returns"
    exact: ClassVar[bool] = True

    def __init__(self, answer: list[Cycle], optimal: bool | None = True, **kwargs) -> None:
        """answer and optimal are returned unchanged by _solve."""
        super().__init__(**kwargs)
        self.answer = answer
        self.optimal = optimal

    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """Return the fixed answer."""
        return list(self.answer), self.optimal, {}


class TwoOnlyDummy(DummySolver):
    """Supports only 2-swaps, like MatchingSolver."""

    name: ClassVar[str] = "two-only"
    supported_lengths: ClassVar[tuple[int, ...]] = (2,)


# ------------------------------------------------------------------------------- __init__


@pytest.mark.parametrize("max_cycle_len", [0, 1, 5])
def test_init_rejects_unsupported_max_cycle_len(max_cycle_len: int) -> None:
    with pytest.raises(ValueError, match="dummy supports max_cycle_len"):
        DummySolver(max_cycle_len=max_cycle_len)


def test_init_uses_the_subclass_supported_lengths() -> None:
    with pytest.raises(ValueError, match=r"two-only supports max_cycle_len in \(2,\), got 3"):
        TwoOnlyDummy()  # default max_cycle_len=3
    assert TwoOnlyDummy(max_cycle_len=2).max_cycle_len == 2


@pytest.mark.parametrize("max_cycle_len", [2, 3, 4])
def test_init_accepts_supported_lengths(max_cycle_len: int) -> None:
    assert DummySolver(max_cycle_len=max_cycle_len).max_cycle_len == max_cycle_len


def test_init_defaults() -> None:
    solver = DummySolver()
    assert solver.max_cycle_len == 3
    assert isinstance(solver.scorer, CountScorer)
    assert solver.time_limit_s is None
    assert solver.seed == 0


def test_init_keeps_given_settings() -> None:
    scorer = ExpectedTransplantScorer(0.9)
    solver = DummySolver(max_cycle_len=2, scorer=scorer, time_limit_s=5.0, seed=7)
    assert solver.scorer is scorer
    assert solver.time_limit_s == 5.0
    assert solver.seed == 7


def test_default_scorers_are_not_shared() -> None:
    assert DummySolver().scorer is not DummySolver().scorer


def test_solver_is_abstract() -> None:
    with pytest.raises(TypeError):
        Solver()  # type: ignore[abstract]


# ------------------------------------------------------------------------- solve: rings in


def test_solve_drops_rings_longer_than_max_before_solve() -> None:
    pool = load_fixture("ring_vs_swap")
    solver = DummySolver(max_cycle_len=2)
    solution = solver.solve(pool, cycles=[RING, SWAP])
    assert solver.seen == [SWAP]
    assert solution.cycles == (SWAP,)


def test_solve_keeps_rings_up_to_max() -> None:
    pool = load_fixture("ring_vs_swap")
    solver = DummySolver(max_cycle_len=3)
    solver.solve(pool, cycles=[RING, SWAP])
    assert solver.seen == [RING, SWAP]


def test_solve_does_not_mutate_the_callers_list() -> None:
    pool = load_fixture("ring_vs_swap")
    rings = [RING, SWAP]
    DummySolver(max_cycle_len=2).solve(pool, cycles=rings)
    assert rings == [RING, SWAP]


def test_solve_finds_rings_when_none_given(monkeypatch: pytest.MonkeyPatch) -> None:
    """With cycles=None, solve calls find_cycles(pool, max_cycle_len). The real finder is the
    Matching owner's, so a fake stands in; patching the module works because solve imports it at call time."""
    pool = load_fixture("ring_vs_swap")
    calls: list[tuple[Pool, int]] = []

    def fake_find_cycles(pool_arg: Pool, max_len: int) -> list[Cycle]:
        calls.append((pool_arg, max_len))
        return [SWAP, RING]

    monkeypatch.setattr(donorbridge.cycles, "find_cycles", fake_find_cycles)
    solution = DummySolver(max_cycle_len=3).solve(pool)
    assert calls == [(pool, 3)]
    assert solution.cycles == (SWAP,)  # first-fit takes the swap, then the ring overlaps it


def test_solve_with_empty_ring_list_skips_find_cycles(monkeypatch: pytest.MonkeyPatch) -> None:
    """cycles=[] means "no rings", not "go and find them"."""

    def must_not_be_called(pool: Pool, max_len: int) -> list[Cycle]:
        raise AssertionError("find_cycles called although cycles were given")

    monkeypatch.setattr(donorbridge.cycles, "find_cycles", must_not_be_called)
    solution = DummySolver().solve(load_fixture("ring_vs_swap"), cycles=[])
    assert solution.cycles == ()


# ---------------------------------------------------------------------- solve: Solution out


def test_solution_fields() -> None:
    pool = load_fixture("ring_vs_swap")
    solution = DummySolver().solve(pool, cycles=[RING, SWAP])
    assert solution.cycles == (RING,)
    assert solution.solver == "dummy"
    assert solution.objective == 3.0
    assert solution.optimal is True
    assert solution.stats == {"seen": 2}
    assert isinstance(solution.runtime_s, float)
    assert solution.runtime_s >= 0.0


def test_solution_rings_are_sorted_by_length_then_families() -> None:
    pool = load_fixture("greedy_trap")
    solution = ReturnsDummy([TRAP_B, TRAP_A], max_cycle_len=3).solve(pool, cycles=[])
    assert solution.cycles == (TRAP_A, TRAP_B)


def test_objective_uses_the_solvers_scorer() -> None:
    pool = load_fixture("ring_vs_swap")
    solver = DummySolver(scorer=ExpectedTransplantScorer(0.9))
    solution = solver.solve(pool, cycles=[RING])
    assert solution.objective == pytest.approx(3 * 0.9**3)
    assert solution.transplants == 3


def test_objective_sums_over_several_rings() -> None:
    pool = load_fixture("greedy_trap")
    solution = DummySolver(scorer=ExpectedTransplantScorer(0.6)).solve(pool, cycles=[TRAP_A, TRAP_B])
    assert solution.objective == pytest.approx(2 * (2 * 0.6**2))


@pytest.mark.parametrize("flag", [True, None, False])
def test_exact_solver_passes_optimal_flag_through(flag: bool | None) -> None:
    pool = load_fixture("ring_vs_swap")
    assert ReturnsDummy([SWAP], optimal=flag).solve(pool, cycles=[]).optimal is flag


def test_heuristic_solver_is_never_optimal() -> None:
    pool = load_fixture("ring_vs_swap")
    solution = HeuristicDummy().solve(pool, cycles=[RING, SWAP])  # its _solve says True
    assert solution.optimal is False
    assert solution.solver == "heuristic-dummy"


def test_empty_pool_gives_empty_solution() -> None:
    solution = DummySolver().solve(load_fixture("empty"), cycles=[])
    assert solution.cycles == ()
    assert solution.objective == 0.0
    assert solution.transplants == 0


# ------------------------------------------------------------------------ solve: validation


def test_solve_rejects_overlapping_rings() -> None:
    pool = load_fixture("ring_vs_swap")
    with pytest.raises(InvalidSolutionError, match="two rings"):
        ReturnsDummy([SWAP, RING]).solve(pool, cycles=[])


def test_solve_rejects_ring_longer_than_max() -> None:
    pool = load_fixture("ring_vs_swap")
    with pytest.raises(InvalidSolutionError, match="allowed 2..2"):
        ReturnsDummy([RING], max_cycle_len=2).solve(pool, cycles=[])


def test_solve_rejects_ring_with_missing_edge() -> None:
    pool = load_fixture("ring_vs_swap")
    with pytest.raises(InvalidSolutionError, match="needs edge 0 -> 2"):
        ReturnsDummy([Cycle.of([0, 2])]).solve(pool, cycles=[])


# ----------------------------------------------------------------------------- weights


def test_weights_count_scorer() -> None:
    pool = load_fixture("ring_vs_swap")
    assert DummySolver().weights(pool, [SWAP, RING]) == {SWAP: 2.0, RING: 3.0}


def test_weights_expected_scorer() -> None:
    pool = load_fixture("ring_vs_swap")
    weights = DummySolver(scorer=ExpectedTransplantScorer(0.6)).weights(pool, [SWAP, RING])
    assert weights[SWAP] == pytest.approx(0.72)
    assert weights[RING] == pytest.approx(3 * 0.6**3)


def test_weights_empty() -> None:
    assert DummySolver().weights(load_fixture("empty"), []) == {}


# ------------------------------------------------------------------------------- __repr__


def test_repr() -> None:
    assert repr(DummySolver()) == "DummySolver(name='dummy', max_cycle_len=3, scorer='count')"
    solver = DummySolver(max_cycle_len=2, scorer=ExpectedTransplantScorer(0.9))
    assert repr(solver) == "DummySolver(name='dummy', max_cycle_len=2, scorer='expected(p=0.9)')"


# ------------------------------------------------------------------------------- registry


def test_registry_keys_match_class_names() -> None:
    for name, cls in SOLVERS.items():
        assert cls.name == name
        assert issubclass(cls, Solver)


def test_get_solver_passes_kwargs() -> None:
    scorer = ExpectedTransplantScorer(0.6)
    solver = get_solver("greedy", max_cycle_len=2, scorer=scorer, time_limit_s=1.5, seed=7)
    assert isinstance(solver, GreedySolver)
    assert solver.max_cycle_len == 2
    assert solver.scorer is scorer
    assert solver.time_limit_s == 1.5
    assert solver.seed == 7


def test_get_solver_unknown_name_lists_valid_names() -> None:
    with pytest.raises(KeyError, match="unknown solver 'nope'") as excinfo:
        get_solver("nope")
    for name in SOLVERS:
        assert name in str(excinfo.value)


def test_get_solver_checks_max_cycle_len() -> None:
    """matching supports only 2-swaps, so the default max_cycle_len=3 is rejected."""
    with pytest.raises(ValueError, match="matching supports max_cycle_len"):
        get_solver("matching")
    assert get_solver("matching", max_cycle_len=2).max_cycle_len == 2
