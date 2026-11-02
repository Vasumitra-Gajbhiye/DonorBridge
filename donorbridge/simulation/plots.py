"""Figures for the report and slides, drawn from the experiment CSVs.

Owner: Simulation
Implemented in: P4
"""

from __future__ import annotations

from pathlib import Path


def make_all_figures(results_dir: Path = Path("results")) -> list[Path]:
    """Read every results/<experiment>.csv present, write one figure per experiment into
    results_dir, and return the paths written. Imports matplotlib inside the function."""
    raise NotImplementedError("Simulation, P4")
