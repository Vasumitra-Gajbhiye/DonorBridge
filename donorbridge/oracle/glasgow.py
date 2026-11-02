"""Loader for the Glasgow kidney-exchange benchmark instances.

Owner: Lead
Implemented in: P2
"""

from __future__ import annotations

from pathlib import Path

from donorbridge.models import Pool


def list_instances(directory: Path) -> list[Path]:
    """Every benchmark instance file in `directory`, sorted by name."""
    raise NotImplementedError("Lead, P2")


def load_glasgow(path: Path) -> Pool:
    """Convert one Glasgow instance into our Pool (ids kept as given, not re-indexed)."""
    raise NotImplementedError("Lead, P2")
