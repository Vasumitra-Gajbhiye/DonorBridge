"""The headline answer: below which survival rate does 3-way stop paying off?

Owner: Lead
Implemented in: P4
"""

from __future__ import annotations

from pathlib import Path


def compute_answer(results_dir: Path = Path("results"), threshold: float = 0.05) -> dict:
    """From results_dir/survival_sweep.csv, find the survival rate p* below which failure-aware
    3-way adds less than `threshold` (relative) over 2-way, interpolating linearly between grid
    points. Writes results_dir/answer.json (threshold_p, gain table, one-sentence answer) and
    returns the same dict."""
    raise NotImplementedError("Lead, P4")
