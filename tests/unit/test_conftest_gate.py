"""Self-test for tests/conftest.py: the stub-skip hook, --gate and --run-slow.

Owner: Lead. Implemented in: P0 (L1.6).

Each test copies our real conftest into a temporary folder (pytester), writes a tiny test file
there, runs pytest on it, and checks the outcome counts.
"""

from __future__ import annotations

from pathlib import Path

import pytest

CONFTEST_SOURCE: str = (Path(__file__).parents[1] / "conftest.py").read_text(encoding="utf-8")

SAMPLE_TESTS: str = """
def test_stub():
    raise NotImplementedError("Lead, P1")

def test_real_bug():
    assert 1 + 1 == 3
"""


@pytest.fixture
def sample(pytester: pytest.Pytester) -> pytest.Pytester:
    """A temp project with our conftest, one stub test and one genuinely failing test."""
    pytester.makeconftest(CONFTEST_SOURCE)
    pytester.makepyfile(test_sample=SAMPLE_TESTS)
    return pytester


def test_stub_is_skipped_without_gate(sample: pytest.Pytester) -> None:
    """Without --gate the stub is skipped (reason names owner and phase); a real failure still fails."""
    result = sample.runpytest("-rs")
    result.assert_outcomes(skipped=1, failed=1)
    result.stdout.fnmatch_lines(["*SKIPPED*stub: Lead, P1*"])


def test_stub_fails_with_gate(sample: pytest.Pytester) -> None:
    """With --gate the stub is a failure, alongside the real failure."""
    result = sample.runpytest("--gate")
    result.assert_outcomes(failed=2)


def test_slow_tests_need_run_slow(pytester: pytest.Pytester) -> None:
    """A test marked slow is skipped by default and runs with --run-slow."""
    pytester.makeconftest(CONFTEST_SOURCE)
    pytester.makeini("[pytest]\nmarkers =\n    slow: long cross-checks (opt-in)\n")
    pytester.makepyfile(
        test_slow="""
import pytest

@pytest.mark.slow
def test_long():
    pass
"""
    )
    pytester.runpytest().assert_outcomes(skipped=1)
    pytester.runpytest("--run-slow").assert_outcomes(passed=1)
