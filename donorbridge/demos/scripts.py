"""Live demos for the presentation.

Owner: Matching
Implemented in: P4
"""

from __future__ import annotations

from collections.abc import Callable


def demo_small() -> None:
    """Walk through a tiny hand-checkable pool: rings found, plan chosen, transplants."""
    raise NotImplementedError("Matching, P4")


def demo_india() -> None:
    """Generate an India pool of 100 and compare 2-way vs 3-way and the heuristics."""
    raise NotImplementedError("Matching, P4")


def demo_edge() -> None:
    """Edge case: a crossmatch fails the night before and the leftover families are re-solved."""
    raise NotImplementedError("Matching, P4")


DEMOS: dict[str, Callable[[], None]] = {
    "small": demo_small,
    "india": demo_india,
    "edge": demo_edge,
}
