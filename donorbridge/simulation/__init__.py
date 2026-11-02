"""Outcome metrics, failure simulation, re-solve, fairness scoring and plots.

Owner: Lead (re-exports only; the modules belong to Simulation)
Implemented in: P1
"""

from donorbridge.simulation.failure import FailureOutcome, FailureSimulator
from donorbridge.simulation.fairness import FairnessScorer
from donorbridge.simulation.metrics import PoolMetrics, compute_metrics
from donorbridge.simulation.plots import make_all_figures
from donorbridge.simulation.resolve import NightBeforeSimulator, ResolveOutcome

__all__ = [
    "FailureOutcome",
    "FailureSimulator",
    "FairnessScorer",
    "NightBeforeSimulator",
    "PoolMetrics",
    "ResolveOutcome",
    "compute_metrics",
    "make_all_figures",
]
