"""Solvers and the name -> class registry.

Owner: Lead
Implemented in: P1
"""

from __future__ import annotations

from typing import Any

from donorbridge.solvers.base import Solver
from donorbridge.solvers.branch_bound import BranchAndBoundSolver
from donorbridge.solvers.brute_force import BruteForceSolver
from donorbridge.solvers.first_come import FirstComeSolver
from donorbridge.solvers.greedy import GreedySolver
from donorbridge.solvers.ilp import ILPSolver
from donorbridge.solvers.local_search import LocalSearchSolver
from donorbridge.solvers.matching import MatchingSolver

SOLVERS: dict[str, type[Solver]] = {
    cls.name: cls
    for cls in (
        FirstComeSolver,
        GreedySolver,
        LocalSearchSolver,
        MatchingSolver,
        BruteForceSolver,
        BranchAndBoundSolver,
        ILPSolver,
    )
}


def get_solver(name: str, **kwargs: Any) -> Solver:
    """Build the solver registered under `name`, passing kwargs to its constructor.

    Raises:
        KeyError: if `name` is unknown; the message lists the valid names.
    """
    if name not in SOLVERS:
        valid = ", ".join(SOLVERS)
        raise KeyError(f"unknown solver {name!r}; valid names: {valid}")
    return SOLVERS[name](**kwargs)


__all__ = [
    "SOLVERS",
    "BranchAndBoundSolver",
    "BruteForceSolver",
    "FirstComeSolver",
    "GreedySolver",
    "ILPSolver",
    "LocalSearchSolver",
    "MatchingSolver",
    "Solver",
    "get_solver",
]
