"""Ring (cycle) enumeration.

Owner: Matching
Implemented in: P1
"""

from __future__ import annotations

from donorbridge.graph import CompatibilityGraph
from donorbridge.models import Cycle, Pool


class CycleFinder:
    """Enumerates every simple ring up to a length cap by depth-first search."""

    def __init__(self, graph: CompatibilityGraph) -> None:
        """Store the graph to search."""
        raise NotImplementedError("Matching, P1")

    def find(self, max_len: int) -> list[Cycle]:
        """Every simple ring with 2 <= len <= max_len, each once (canonical form),
        sorted by (len, families)."""
        raise NotImplementedError("Matching, P1")


def find_cycles(pool: Pool, max_len: int) -> list[Cycle]:
    """Convenience wrapper: CycleFinder(CompatibilityGraph(pool)).find(max_len)."""
    raise NotImplementedError("Matching, P1")


def find_cycles_nested_loops(pool: Pool, max_len: int) -> list[Cycle]:
    """Reference enumeration with explicit nested loops, for cross-checking find_cycles.
    Supports max_len <= 3 only. Same output order as find_cycles."""
    raise NotImplementedError("Matching, P1")
