"""Shared pytest configuration for DonorBridge.

Owner: Lead. Implemented in: P0 (L1.6).

Provides:
- load_fixture(name) / load_expected(name): read the hand-built pools in tests/fixtures/.
  Import them in a test with `from conftest import load_fixture, load_expected`.
- --run-slow: tests marked @pytest.mark.slow are skipped unless this flag is given.
- --gate: turns "stub" skips back into failures (used at each phase gate).
- The stub-skip hook: a test whose body hits an unfinished stub (NotImplementedError)
  is reported as skipped, not failed, unless --gate is given.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from donorbridge.models import Pool

# Lets tests/unit/test_conftest_gate.py run a throwaway pytest session in a temp folder.
pytest_plugins = ["pytester"]

FIXTURES_DIR: Path = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> Pool:
    """Load the pool stored in tests/fixtures/<name>.json, e.g. load_fixture("pool_8")."""
    return Pool.load_json(FIXTURES_DIR / f"{name}.json")


def load_expected(name: str) -> dict:
    """Load the known answers in tests/fixtures/<name>.expected.json, e.g. load_expected("pool_8")."""
    path = FIXTURES_DIR / f"{name}.expected.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register the --run-slow and --gate command-line flags."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="also run tests marked @pytest.mark.slow",
    )
    parser.addoption(
        "--gate",
        action="store_true",
        default=False,
        help="phase gate: unfinished stubs (NotImplementedError) fail instead of skipping",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Without --run-slow, add a skip marker to every test marked slow."""
    if config.getoption("--run-slow"):
        return
    skip_slow = pytest.mark.skip(reason="slow test: pass --run-slow to run it")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> pytest.TestReport:
    """Report a test that hit an unfinished stub as skipped, unless --gate is set.

    How it works:
    1. pytest builds a report for each phase (setup, call, teardown); `yield` hands us that report.
    2. If the test body ("call") failed with NotImplementedError and --gate is off, we relabel it
       "skipped" with reason "stub: <message>", e.g. "stub: Lead, P1" (owner and phase).
    3. With --gate, or for any other exception or phase, the report is returned unchanged.
    """
    report: pytest.TestReport = yield
    hit_stub = (
        call.when == "call"
        and report.failed
        and call.excinfo is not None
        and call.excinfo.errisinstance(NotImplementedError)
    )
    if hit_stub and not item.config.getoption("--gate"):
        report.outcome = "skipped"
        # A skipped report's longrepr is (file, 1-based line, reason); `pytest -rs` prints it.
        file, line0, _ = item.location
        report.longrepr = (file, line0 + 1, f"stub: {call.excinfo.value}")
    return report
