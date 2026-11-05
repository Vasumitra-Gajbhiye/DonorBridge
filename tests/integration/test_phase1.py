"""Phase 1 integration tests: the definition of done for P1 Foundations.

Owner: Lead. Implemented in: P1 (L1.7). Spec: team/01_lead.md, "Integration test spec: Phase 1".

Every test name starts with test_p1_<role>_ or test_p1_e2e_, so each teammate can run only theirs:
    uv run pytest tests/integration/test_phase1.py -k generator -rs
A test whose code is still a stub (NotImplementedError) shows as skipped; the phase gate
(`uv run pytest tests/unit tests/integration/test_phase1.py --gate`) turns those skips into failures.

Rules this file follows:
- Stubs are only ever called inside test bodies, never in a @pytest.fixture: the stub-skip hook in
  tests/conftest.py only relabels the "call" phase, so a stub hit during setup would be an error.
- Randomness always comes from a fixed seed. Floats are compared with pytest.approx.
- Ids are never used as indices: families are looked up with pool.family(fid).
- The whole file should run in well under 30 s.
"""

from __future__ import annotations

import importlib
import json
import math
import time
from collections.abc import Iterable, Sequence

import pytest
from conftest import load_expected, load_fixture

from donorbridge.compatibility import blood_compatible
from donorbridge.cycles import find_cycles, find_cycles_nested_loops
from donorbridge.generator import make_generator
from donorbridge.graph import CompatibilityGraph
from donorbridge.models import BloodGroup, Cycle, InvalidSolutionError, Pool, Solution
from donorbridge.scoring import ExpectedTransplantScorer
from donorbridge.simulation import FailureSimulator, compute_metrics
from donorbridge.solvers import SOLVERS, Solver, get_solver
from donorbridge.survival import UniformSurvival

SEED: int = 2026

ALL_FIXTURES: tuple[str, ...] = ("pool_8", "ring_vs_swap", "greedy_trap", "empty", "no_edges")

SOLVER_NAMES: tuple[str, ...] = (
    "first-come",
    "greedy",
    "local-search",
    "matching",
    "brute-force",
    "branch-bound",
    "ilp",
)

# The unique optimum of pool_8 with rings of up to 3 (report/01_lead/04_fixtures.md, section 2.3).
POOL_8_OPT_L3: tuple[tuple[int, ...], ...] = ((3, 12), (9, 14), (5, 7, 21))

# Every module in the module map (team/01_lead.md, section 5), packages included.
MODULE_MAP: tuple[str, ...] = (
    "donorbridge",
    "donorbridge.__main__",
    "donorbridge.models",
    "donorbridge.survival",
    "donorbridge.scoring",
    "donorbridge.compatibility",
    "donorbridge.graph",
    "donorbridge.cycles",
    "donorbridge.solvers",
    "donorbridge.solvers.base",
    "donorbridge.solvers.first_come",
    "donorbridge.solvers.greedy",
    "donorbridge.solvers.local_search",
    "donorbridge.solvers.matching",
    "donorbridge.solvers.brute_force",
    "donorbridge.solvers.branch_bound",
    "donorbridge.solvers.ilp",
    "donorbridge.generator",
    "donorbridge.generator.calibration",
    "donorbridge.generator.saidman",
    "donorbridge.generator.report",
    "donorbridge.generator.survival_models",
    "donorbridge.generator.regions",
    "donorbridge.simulation",
    "donorbridge.simulation.metrics",
    "donorbridge.simulation.failure",
    "donorbridge.simulation.resolve",
    "donorbridge.simulation.fairness",
    "donorbridge.simulation.plots",
    "donorbridge.experiments",
    "donorbridge.experiments.grid",
    "donorbridge.experiments.survival_sweep",
    "donorbridge.experiments.blood_mix",
    "donorbridge.experiments.female_sensitisation",
    "donorbridge.experiments.regions",
    "donorbridge.experiments.cycle_growth",
    "donorbridge.experiments.optimality_gap",
    "donorbridge.experiments.ring_length",
    "donorbridge.experiments.fairness",
    "donorbridge.experiments.runtime",
    "donorbridge.experiments.answer",
    "donorbridge.oracle",
    "donorbridge.oracle.glasgow",
    "donorbridge.oracle.kep_oracle",
    "donorbridge.oracle.crosscheck",
    "donorbridge.demos",
    "donorbridge.demos.scripts",
)


# ----------------------------------------------------------------------------------- helpers


def rings_as_lists(rings: Iterable[Cycle]) -> list[list[int]]:
    """Rings as plain lists, the format used in the *.expected.json files."""
    return [list(ring.families) for ring in rings]


def hand_solution(rings: Sequence[Sequence[int]]) -> Solution:
    """A plan built by hand, with no solver involved. Rings are sorted the way Solver.solve sorts them."""
    cycles = sorted((Cycle.of(ring) for ring in rings), key=lambda c: (len(c), c.families))
    return Solution(
        cycles=tuple(cycles),
        solver="hand",
        objective=float(sum(len(ring) for ring in rings)),
        runtime_s=0.0,
        optimal=None,
    )


def india_pools(n_pools: int, n: int, seed: int = SEED) -> list[Pool]:
    """n_pools India pools of n families each, using seeds seed, seed+1, ..."""
    return make_generator("india").generate_many(n_pools, n, seed)


def check_heuristic_plan(solver: Solver, pool: Pool, max_cycle_len: int) -> None:
    """Solve `pool` and check the plan is valid and flagged as not proven optimal."""
    solution = solver.solve(pool)
    solution.validate(pool, max_cycle_len)
    assert solution.solver == solver.name, pool.name
    assert solution.optimal is False, pool.name


# -------------------------------------------------------------------------------------- lead


def test_p1_lead_all_modules_import() -> None:
    """Every module in the module map imports."""
    for module in MODULE_MAP:
        importlib.import_module(module)


def test_p1_lead_registry_has_seven_solvers() -> None:
    """SOLVERS has exactly the seven contract names; an unknown name raises KeyError listing them."""
    assert set(SOLVERS) == set(SOLVER_NAMES)
    with pytest.raises(KeyError, match="greedy"):
        get_solver("x")


def test_p1_lead_pool_json_roundtrip() -> None:
    """Every fixture survives to_dict -> from_dict, directly and through JSON text."""
    for name in ALL_FIXTURES:
        pool = load_fixture(name)
        assert Pool.from_dict(pool.to_dict()) == pool, name
        as_text = json.dumps(pool.to_dict())  # to_dict must be JSON-ready (enums as values)
        assert Pool.from_dict(json.loads(as_text)) == pool, name


def test_p1_lead_cycle_canonical_form() -> None:
    """Any rotation gives the same ring (smallest id first); the opposite direction is a different ring."""
    assert Cycle.of([3, 1, 2]) == Cycle.of([1, 2, 3])
    assert Cycle.of([2, 3, 1]).families == (1, 2, 3)
    assert Cycle.of([3, 1, 2]) != Cycle.of([1, 3, 2])


def test_p1_lead_validate_rejects_bad_solutions() -> None:
    """Overlap, missing edge, too long and unknown id each raise InvalidSolutionError on pool_8."""
    pool = load_fixture("pool_8")
    hand_solution(POOL_8_OPT_L3).validate(pool, max_cycle_len=3)  # control: a valid plan passes

    bad_plans: dict[str, tuple[list[tuple[int, ...]], int]] = {
        "overlap": ([(3, 12), (3, 12, 7)], 3),  # families 3 and 12 are in both rings
        "missing edge": ([(1, 3)], 3),  # 1 -> 3 exists, 3 -> 1 does not
        "too long": ([(3, 12, 7)], 2),  # a real ring of 3, but the cap is 2
        "unknown id": ([(3, 99)], 3),  # pool_8 has no family 99
    }
    for reason, (rings, max_cycle_len) in bad_plans.items():
        try:
            hand_solution(rings).validate(pool, max_cycle_len)
        except InvalidSolutionError:
            continue
        pytest.fail(f"validate accepted a bad plan ({reason}): {rings}")


def test_p1_lead_expected_weights_crossover() -> None:
    """ring_vs_swap: the 3-ring (0,1,2) outweighs the swap (0,1) exactly when p > 2/3."""
    pool = load_fixture("ring_vs_swap")
    swap, ring = Cycle.of([0, 1]), Cycle.of([0, 1, 2])
    for p in (0.5, 0.6, 0.66, 0.67, 0.7, 0.9, 1.0):
        scorer = ExpectedTransplantScorer(p)
        w_swap, w_ring = scorer.weight(swap, pool), scorer.weight(ring, pool)
        assert w_swap == pytest.approx(2 * p**2), p  # p = 0.6: 0.72
        assert w_ring == pytest.approx(3 * p**3), p  # p = 0.6: 0.648
        assert (w_ring > w_swap) == (p > 2 / 3), p

    at_crossover = ExpectedTransplantScorer(2 / 3)  # 2 * (2/3)^2 == 3 * (2/3)^3 == 8/9: a tie
    assert at_crossover.weight(ring, pool) == pytest.approx(at_crossover.weight(swap, pool))

    from_model = ExpectedTransplantScorer(UniformSurvival(0.6))  # a float p means UniformSurvival(p)
    assert from_model.weight(ring, pool) == pytest.approx(ExpectedTransplantScorer(0.6).weight(ring, pool))


# --------------------------------------------------------------------------------- generator


def test_p1_generator_deterministic() -> None:
    """Same seed gives equal pools (same or fresh generator); a different seed gives a different pool."""
    generator = make_generator("india")
    first = generator.generate(100, seed=1)
    assert generator.generate(100, seed=1) == first  # same generator, called again
    assert make_generator("india").generate(100, seed=1) == first  # a fresh generator

    other = generator.generate(100, seed=2)
    # Compare contents, not names: a name such as "india-n100-s2" differs even if the data does not.
    assert (other.families, other.edges) != (first.families, first.edges)


def test_p1_generator_pool_shape() -> None:
    """India n=100: 100 families, unique ids, no self-edges, every edge ABO-compatible."""
    pool = make_generator("india").generate(100, seed=SEED)
    ids = [family.id for family in pool.families]
    assert pool.n == 100
    assert len(ids) == 100
    assert len(set(ids)) == 100
    for i, j in pool.edges:
        assert i != j
        donor, patient = pool.family(i).donor_blood, pool.family(j).patient_blood
        assert blood_compatible(donor, patient), (i, j, donor, patient)


def test_p1_generator_selection_effect() -> None:
    """Over 20 India pools of 100, O patients are over-represented and O donors under-represented."""
    families = [family for pool in india_pools(20, 100) for family in pool.families]
    share_o_patients = sum(f.patient_blood == BloodGroup.O for f in families) / len(families)
    share_o_donors = sum(f.donor_blood == BloodGroup.O for f in families) / len(families)
    assert share_o_patients > share_o_donors


def test_p1_generator_report_consistent() -> None:
    """pairs_sampled == n + rejected_compatible, and generate() returns the same pool as the report call."""
    generator = make_generator("india")
    for seed in (SEED, SEED + 1):
        pool, report = generator.generate_with_report(100, seed)
        assert pool.n == 100
        assert report.pairs_sampled == 100 + report.rejected_compatible, seed
        assert generator.generate(100, seed) == pool, seed


# ---------------------------------------------------------------------------------- matching


def test_p1_matching_graph_matches_edges() -> None:
    """On every fixture, nodes/successors/predecessors/has_edge agree with pool.edges."""
    for name in ALL_FIXTURES:
        pool = load_fixture(name)
        graph = CompatibilityGraph(pool)
        assert graph.nodes() == pool.ids(), name
        for fid in pool.ids():
            successors = tuple(sorted(j for i, j in pool.edges if i == fid))
            predecessors = tuple(sorted(i for i, j in pool.edges if j == fid))
            assert graph.successors(fid) == successors, (name, fid)
            assert graph.predecessors(fid) == predecessors, (name, fid)
            for other in pool.ids():
                assert graph.has_edge(fid, other) == ((fid, other) in pool.edges), (name, fid, other)


def test_p1_matching_rings_on_fixtures() -> None:
    """find_cycles reproduces pool_8.expected.json and the rings listed in section 5 of the playbook."""
    pool_8, expected = load_fixture("pool_8"), load_expected("pool_8")
    assert rings_as_lists(find_cycles(pool_8, 2)) == expected["rings_L2"]
    assert rings_as_lists(find_cycles(pool_8, 3)) == expected["rings_L3"]  # includes the 2-rings

    # Sorted by (len, families).
    assert rings_as_lists(find_cycles(load_fixture("ring_vs_swap"), 3)) == [[0, 1], [0, 1, 2]]
    assert rings_as_lists(find_cycles(load_fixture("greedy_trap"), 3)) == [[0, 3], [1, 2], [0, 1, 2]]
    for name in ("empty", "no_edges"):
        assert find_cycles(load_fixture(name), 3) == [], name


def test_p1_matching_dfs_equals_nested_loops() -> None:
    """20 India pools of 60, L=3: the DFS and the nested-loop reference return identical lists."""
    rings_seen = 0
    for pool in india_pools(20, 60):
        dfs = find_cycles(pool, 3)
        assert dfs == find_cycles_nested_loops(pool, 3), pool.name
        rings_seen += len(dfs)
    assert rings_seen > 0  # guard: the comparison means nothing if no pool has a ring


# -------------------------------------------------------------------------------- heuristics


def test_p1_heuristics_first_come_valid() -> None:
    """First-come on every fixture and on 10 India pools: the plan validates and optimal is False."""
    solver = get_solver("first-come", max_cycle_len=3)
    for name in ALL_FIXTURES:  # fixtures first: they need no generator
        check_heuristic_plan(solver, load_fixture(name), max_cycle_len=3)
    for pool in india_pools(10, 60):
        check_heuristic_plan(solver, pool, max_cycle_len=3)


def test_p1_heuristics_greedy_on_fixtures() -> None:
    """Greedy (count): greedy_trap -> 3 transplants; ring_vs_swap -> the ring; empty and no_edges -> 0 rings."""
    greedy = get_solver("greedy", max_cycle_len=3)  # default scorer: CountScorer

    trap = greedy.solve(load_fixture("greedy_trap"))
    assert trap.cycles == (Cycle.of([0, 1, 2]),)  # takes the 3-ring; the optimum (0,3)+(1,2) is 4
    assert trap.transplants == 3
    assert trap.objective == pytest.approx(3.0)

    ring_or_swap = greedy.solve(load_fixture("ring_vs_swap"))
    assert ring_or_swap.cycles == (Cycle.of([0, 1, 2]),)  # count weight: 3 > 2

    for name in ("empty", "no_edges"):
        assert greedy.solve(load_fixture(name)).cycles == (), name


# -------------------------------------------------------------------------------- simulation


def test_p1_simulation_metrics_on_fixture() -> None:
    """pool_8 with its L=3 optimum (3,12)+(9,14)+(5,7,21): every count worked out by hand."""
    pool, plan = load_fixture("pool_8"), hand_solution(POOL_8_OPT_L3)
    metrics = compute_metrics(pool, plan)  # survival defaults to UniformSurvival(1.0)

    assert metrics.n_families == 8
    assert metrics.transplants == 7
    assert metrics.expected_transplants == pytest.approx(7.0)
    assert {length: count for length, count in metrics.rings_by_len.items() if count} == {2: 2, 3: 1}
    # Highly sensitised: 21 (PRA exactly 0.80) is matched, 1 (PRA 0.92) is not.
    assert (metrics.hs_matched, metrics.hs_total) == (1, 2)
    # Female patients 1, 5, 7, 14: all but 1 matched. Male patients 3, 9, 12, 21: all matched.
    assert (metrics.female_matched, metrics.female_total) == (3, 4)
    assert (metrics.male_matched, metrics.male_total) == (4, 4)
    assert metrics.hs_matched_share == pytest.approx(0.5)
    assert metrics.female_matched_share == pytest.approx(0.75)
    assert metrics.male_matched_share == pytest.approx(1.0)
    # Patient blood: O = {1}; A = {3, 7, 9, 21}; B = {5, 12, 14}. Values are (matched, total).
    assert metrics.by_blood["O"] == (0, 1)
    assert metrics.by_blood["A"] == (4, 4)
    assert metrics.by_blood["B"] == (3, 3)

    at_half = compute_metrics(pool, plan, UniformSurvival(0.5))
    assert at_half.expected_transplants == pytest.approx(2 * 0.5**2 + 2 * 0.5**2 + 3 * 0.5**3)  # 1.375


def test_p1_simulation_failure_p1_exact() -> None:
    """UniformSurvival(1.0): every draw realises every ring, so the Monte Carlo mean is exact."""
    pool, plan = load_fixture("pool_8"), hand_solution(POOL_8_OPT_L3)
    simulator = FailureSimulator(UniformSurvival(1.0), seed=SEED)
    for _ in range(200):
        outcome = simulator.realise(pool, plan)
        assert outcome.went_ahead == plan.cycles
        assert outcome.cancelled == ()
        assert outcome.failed_edges == frozenset()
        assert outcome.transplants == 7

    mean, half_width = simulator.expected(pool, plan, n_trials=500)
    assert mean == pytest.approx(7.0)
    assert half_width == pytest.approx(0.0)


def test_p1_simulation_failure_matches_analytic() -> None:
    """p=0.7, 20,000 trials on greedy's pool_8 plan: |mean - sum |c| p^|c|| < 3 standard errors."""
    p, n_trials = 0.7, 20_000
    pool = load_fixture("pool_8")
    plan = get_solver("greedy", max_cycle_len=3).solve(pool)
    assert plan.cycles  # guard: an empty plan would make the check trivial

    # Ring c goes ahead with probability q = p^|c| and then gives |c| transplants. Rings share no
    # family, hence no edge, so they are independent and their variances |c|^2 q (1 - q) add up.
    analytic = sum(len(c) * p ** len(c) for c in plan.cycles)
    variance = sum(len(c) ** 2 * p ** len(c) * (1 - p ** len(c)) for c in plan.cycles)
    standard_error = math.sqrt(variance / n_trials)

    mean, half_width = FailureSimulator(UniformSurvival(p), seed=SEED).expected(pool, plan, n_trials)
    assert abs(mean - analytic) < 3 * standard_error
    # The reported 95% half-width should be 1.96 standard errors (sample sd is within 1% at this n).
    assert half_width == pytest.approx(1.96 * standard_error, rel=0.1)


# -------------------------------------------------------------------------------- end to end


def test_p1_e2e_pipeline_india_100() -> None:
    """generate -> find_cycles -> greedy -> validate -> metrics -> simulate on India n=100, in < 10 s."""
    p = 0.7
    start = time.perf_counter()
    pool = make_generator("india").generate(100, seed=SEED)
    rings = find_cycles(pool, 3)
    plan = get_solver("greedy", max_cycle_len=3).solve(pool, cycles=rings)
    plan.validate(pool, max_cycle_len=3)
    metrics = compute_metrics(pool, plan, UniformSurvival(p))
    mean, half_width = FailureSimulator(UniformSurvival(p), seed=SEED).expected(pool, plan, n_trials=2_000)
    elapsed = time.perf_counter() - start

    assert elapsed < 10.0
    assert plan.transplants > 0
    assert set(plan.cycles) <= set(rings)  # greedy chose only from the rings it was given
    assert metrics.n_families == 100
    assert metrics.transplants == plan.transplants
    expected = ExpectedTransplantScorer(p).total(plan.cycles, pool)
    assert metrics.expected_transplants == pytest.approx(expected)
    # The simulated mean agrees with the formula, within 4 standard errors (half_width = 1.96 SE).
    assert abs(mean - expected) <= 4 * half_width / 1.96


def test_p1_e2e_solver_names_resolve() -> None:
    """Every registry name builds its solver via get_solver; first-come and greedy solve pool_8."""
    for name in SOLVER_NAMES:
        solver_class = SOLVERS[name]
        # matching supports only rings of 2, so the default max_cycle_len=3 would be rejected.
        max_cycle_len = 3 if 3 in solver_class.supported_lengths else max(solver_class.supported_lengths)
        assert isinstance(get_solver(name, max_cycle_len=max_cycle_len), solver_class), name

    pool = load_fixture("pool_8")
    for name in ("first-come", "greedy"):
        solution = get_solver(name, max_cycle_len=3).solve(pool)
        solution.validate(pool, max_cycle_len=3)
        assert solution.solver == name
        assert solution.transplants > 0
