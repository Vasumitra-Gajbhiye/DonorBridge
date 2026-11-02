"""Independent oracle: solve our Pool with the external kep_solver package.

Owner: Lead
Implemented in: P2
"""

from __future__ import annotations

from donorbridge.models import Pool


def kep_optimum(pool: Pool, max_cycle_len: int) -> int:
    """Maximum transplants (count objective, no chains) according to kep_solver.

    kep_solver is imported lazily inside this function, so the package never needs it; install it
    with `uv sync --extra oracle`.
    """
    raise NotImplementedError("Lead, P2")
