"""Unit tests for donorbridge.survival and donorbridge.scoring."""

from __future__ import annotations

import math

import pytest
from conftest import load_fixture

from donorbridge.models import Cycle, Pool
from donorbridge.scoring import CountScorer, ExpectedTransplantScorer, Scorer
from donorbridge.survival import SurvivalModel, UniformSurvival

# ring_vs_swap: families 0, 1, 2; edges 0->1, 1->0, 1->2, 2->0.
# Its two rings share families 0 and 1, so a plan can use only one of them.
SWAP = Cycle.of([0, 1])
RING = Cycle.of([0, 1, 2])


class PerEdgeSurvival(SurvivalModel):
    """Test-only model: each directed edge has its own survival chance."""

    def __init__(self, chances: dict[tuple[int, int], float]) -> None:
        """chances maps (donor_family, patient_family) to P(crossmatch passes)."""
        self.chances = chances

    def edge(self, pool: Pool, donor_family: int, patient_family: int) -> float:
        """Look the edge up in the table."""
        return self.chances[(donor_family, patient_family)]


# ---------------------------------------------------------------- UniformSurvival


@pytest.mark.parametrize("p", [-0.1, 1.1, math.nan])
def test_uniform_survival_rejects_p_outside_0_1(p: float) -> None:
    with pytest.raises(ValueError, match="p must be in"):
        UniformSurvival(p)


@pytest.mark.parametrize("p", [0, 0.0, 0.5, 1, 1.0])
def test_uniform_survival_accepts_bounds(p: float) -> None:
    assert UniformSurvival(p).p == p


def test_uniform_edge_returns_p_for_every_edge() -> None:
    pool = load_fixture("ring_vs_swap")
    survival = UniformSurvival(0.7)
    assert all(survival.edge(pool, i, j) == 0.7 for i, j in pool.edges)


def test_uniform_cycle_is_p_to_the_ring_length() -> None:
    pool = load_fixture("ring_vs_swap")
    survival = UniformSurvival(0.8)
    assert survival.cycle(pool, SWAP) == pytest.approx(0.8**2)
    assert survival.cycle(pool, RING) == pytest.approx(0.8**3)


# ---------------------------------------------------------------- SurvivalModel.cycle


def test_cycle_multiplies_edge_over_the_ring_edges_in_direction() -> None:
    pool = load_fixture("ring_vs_swap")
    survival = PerEdgeSurvival({(0, 1): 0.9, (1, 2): 0.5, (2, 0): 0.4, (1, 0): 0.2})
    # The ring (0, 1, 2) uses 0->1, 1->2, 2->0; it never touches 1->0.
    assert survival.cycle(pool, RING) == pytest.approx(0.9 * 0.5 * 0.4)
    # The swap uses both directions between 0 and 1.
    assert survival.cycle(pool, SWAP) == pytest.approx(0.9 * 0.2)


# ---------------------------------------------------------------- ExpectedTransplantScorer weights


def test_three_ring_weight_at_p_0_9() -> None:
    pool = load_fixture("ring_vs_swap")
    assert ExpectedTransplantScorer(0.9).weight(RING, pool) == pytest.approx(3 * 0.9**3)  # 2.187


def test_two_ring_weight_at_p_0_6() -> None:
    pool = load_fixture("ring_vs_swap")
    assert ExpectedTransplantScorer(0.6).weight(SWAP, pool) == pytest.approx(0.72)  # 2 * 0.36


@pytest.mark.parametrize("p", [0.5, 0.6, 0.66, 0.67, 0.7, 0.9])
def test_ring_beats_swap_iff_p_above_two_thirds(p: float) -> None:
    """3 p^3 > 2 p^2  <=>  p > 2/3 (for p > 0)."""
    pool = load_fixture("ring_vs_swap")
    scorer = ExpectedTransplantScorer(p)
    ring_wins = scorer.weight(RING, pool) > scorer.weight(SWAP, pool)
    assert ring_wins == (p > 2 / 3)


def test_float_argument_becomes_uniform_survival() -> None:
    pool = load_fixture("ring_vs_swap")
    from_float = ExpectedTransplantScorer(0.6)
    from_model = ExpectedTransplantScorer(UniformSurvival(0.6))
    assert isinstance(from_float.survival, UniformSurvival)
    assert from_float.survival.p == 0.6
    assert from_float.weight(RING, pool) == pytest.approx(from_model.weight(RING, pool))


def test_expected_scorer_rejects_bad_float() -> None:
    with pytest.raises(ValueError, match="p must be in"):
        ExpectedTransplantScorer(1.5)


# ---------------------------------------------------------------- CountScorer


def test_count_scorer_ignores_p() -> None:
    pool = load_fixture("ring_vs_swap")
    count = CountScorer()
    assert count.weight(SWAP, pool) == 2.0
    assert count.weight(RING, pool) == 3.0
    # Count is expected-transplant scoring with no failures, and it picks the ring at every p.
    certain = ExpectedTransplantScorer(1.0)
    assert count.weight(SWAP, pool) == certain.weight(SWAP, pool)
    assert count.weight(RING, pool) == certain.weight(RING, pool)


# ---------------------------------------------------------------- Scorer.total


def test_total_sums_weights_over_rings() -> None:
    pool = load_fixture("ring_vs_swap")
    rings = [SWAP, RING]  # overlapping, but total() only adds; it does not validate
    assert CountScorer().total(rings, pool) == 5.0
    assert ExpectedTransplantScorer(0.6).total(rings, pool) == pytest.approx(0.72 + 3 * 0.6**3)


def test_total_of_empty_plan_is_float_zero() -> None:
    pool = load_fixture("ring_vs_swap")
    for scorer in (CountScorer(), ExpectedTransplantScorer(0.6)):
        total = scorer.total([], pool)
        assert total == 0.0 and isinstance(total, float)


def test_total_accepts_any_iterable() -> None:
    pool = load_fixture("ring_vs_swap")
    assert CountScorer().total((ring for ring in [SWAP, RING]), pool) == 5.0


# ---------------------------------------------------------------- names


def test_scorer_names() -> None:
    assert CountScorer().name == "count"
    assert ExpectedTransplantScorer().name == "expected(p=1.0)"
    assert ExpectedTransplantScorer(0.6).name == "expected(p=0.6)"
    assert ExpectedTransplantScorer(1).name == "expected(p=1.0)"  # int p is stored as float
    assert ExpectedTransplantScorer(UniformSurvival(0.9)).name == "expected(p=0.9)"
    assert ExpectedTransplantScorer(PerEdgeSurvival({})).name == "expected(PerEdgeSurvival)"


def test_abstract_classes_cannot_be_built() -> None:
    with pytest.raises(TypeError):
        Scorer()  # type: ignore[abstract]
    with pytest.raises(TypeError):
        SurvivalModel()  # type: ignore[abstract]
