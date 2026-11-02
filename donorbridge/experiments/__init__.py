"""Experiments: the grid engine, every experiment SPEC, and the headline answer.

Owner: Lead (re-exports only; each module has its own owner)
Implemented in: P1
"""

from donorbridge.experiments import (
    blood_mix,
    cycle_growth,
    fairness,
    female_sensitisation,
    optimality_gap,
    regions,
    ring_length,
    runtime,
    survival_sweep,
)
from donorbridge.experiments.answer import compute_answer
from donorbridge.experiments.grid import ROW_COLUMNS, GridSpec, Setting, run_grid

EXPERIMENTS: dict[str, GridSpec] = {
    m.SPEC.name: m.SPEC
    for m in (
        survival_sweep,
        blood_mix,
        female_sensitisation,
        regions,
        cycle_growth,
        optimality_gap,
        ring_length,
        fairness,
        runtime,
    )
}

__all__ = [
    "EXPERIMENTS",
    "ROW_COLUMNS",
    "GridSpec",
    "Setting",
    "compute_answer",
    "run_grid",
]
