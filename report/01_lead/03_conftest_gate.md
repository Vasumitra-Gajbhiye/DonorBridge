# Report 03 (Lead): tests/conftest.py with the stub-skip hook (L1.6)

**Date:** 2026-11-03
**Owner:** Lead
**Status:** Done locally and verified. Not yet committed.

## 1. What was asked

1. `load_fixture(name) -> Pool` (reads `tests/fixtures/<name>.json`) and `load_expected(name) -> dict`.
2. Command-line options `--run-slow` (tests marked `slow` are skipped without it) and `--gate`.
3. A `pytest_runtest_makereport` hook: if a test's call phase raised `NotImplementedError` and
   `--gate` is off, rewrite the report as skipped with reason `stub: <message>`. With `--gate`,
   leave it as a failure. Explain the hook in 3 lines.
4. A small pytester self-test in `tests/unit/test_conftest_gate.py` proving both behaviours.

## 2. What was done

| File | Contents |
|---|---|
| `tests/conftest.py` | `FIXTURES_DIR`, `load_fixture`, `load_expected`, `pytest_addoption`, `pytest_collection_modifyitems` (slow skip), the `pytest_runtest_makereport` wrapper, and `pytest_plugins = ["pytester"]` |
| `tests/unit/test_conftest_gate.py` | 3 tests that copy the real conftest into a pytester temp folder and run pytest there |

**The hook in 3 lines** (also in its docstring):

1. pytest builds a report for each phase (setup, call, teardown); `yield` hands us that report.
2. If the test body (`call`) failed with `NotImplementedError` and `--gate` is off, we relabel it
   `skipped` with reason `stub: <message>`, e.g. `stub: Lead, P1`.
3. With `--gate`, or for any other exception or phase, the report is returned unchanged.

**Self-tests:**

| Test | Proves |
|---|---|
| `test_stub_is_skipped_without_gate` | stub → skipped and `-rs` shows `stub: Lead, P1`; a plain `assert` failure still fails |
| `test_stub_fails_with_gate` | with `--gate`, both the stub and the real bug fail |
| `test_slow_tests_need_run_slow` | `@pytest.mark.slow` is skipped by default and passes with `--run-slow` |

**Verification:**

```bash
uv run pytest tests/unit -v     # 3 passed in 0.10s (each test ≈ 0.02 s)
uv run pytest -q                # 3 passed
```

I also ran a throwaway probe (deleted afterwards) that calls `load_fixture("pool_8")` from a real
test file. While `Pool.load_json` is still a stub, it printed
`SKIPPED [1] tests/unit/test_zz_probe.py:2: stub: Lead, P1`, and with `--gate` it printed
`FAILED ... NotImplementedError: Lead, P1`. So the whole chain works end to end.

## 3. Deviations from the request or the contract

1. **Extra self-test for `--run-slow`.** Not asked for in item 4, but it is the other flag the
   conftest adds and it costs 0.03 s.
2. **The hook only rewrites reports that actually failed** (`report.failed`). Without this check, an
   `xfail` test that raises `NotImplementedError` (already reported as an expected failure) would be
   relabelled as a stub skip.
3. **`pytest_plugins = ["pytester"]` lives in `tests/conftest.py`.** pytester has to be enabled
   somewhere, and the conftest is the file I own. Nothing in `pyproject.toml` changed.
4. **No contract change.**

## 4. Things to note

1. **Environment fix: the editable install was stale.** `uv run pytest` could not import
   `donorbridge`. The editable install was built in L1.0, before `donorbridge/` existed, so its
   finder had an empty `MAPPING`. (`uv run python -c "import donorbridge"` worked only because the
   current directory is on `sys.path`.) I fixed it with `uv sync --reinstall-package donorbridge`,
   then ran `uv sync --extra oracle` to put back kep_solver, which plain `uv sync` had removed.
   `pyproject.toml` and `uv.lock` are unchanged. CI is not affected, because it runs a fresh
   `uv sync --locked`. **Teammates who ran `uv sync` before the skeleton commit will hit the same
   `ModuleNotFoundError`**, and should run `uv sync --reinstall-package donorbridge`. Worth adding to
   the group-chat post.
2. **How tests use the loaders:** `from conftest import load_fixture, load_expected`. This works
   because pytest's default import mode puts `tests/` on `sys.path` when it loads the conftest.
3. **Only the call phase is caught.** If a teammate wraps `load_fixture` (or any other stub) in a
   `@pytest.fixture`, the `NotImplementedError` happens during *setup* and shows as an **error**, not
   a skip. That is what the task asked for, but tell teammates to call stubs inside the test body.
4. **Any `NotImplementedError` counts as a stub**, including one from an abstract method that a
   subclass forgot to override. That is fine: `--gate` still catches it.
5. **`load_expected("pool_8")` reads `pool_8.expected.json`**, matching the fixtures table. No
   fixture files exist yet (L1.5).
6. **CI should now pass the unit step.** The integration step will still fail with "no tests
   collected" until `tests/integration/test_phase1.py` exists (L1.7).

## 5. Next steps

- [ ] L1.5 fixtures: `pool_8`, `ring_vs_swap`, `greedy_trap`, `empty`, `no_edges`.
- [ ] L1.7 `tests/integration/test_phase1.py`, so the CI integration step has something to collect.
- [ ] Commit the P0 work to `main` and post in the group chat, including the
      `uv sync --reinstall-package donorbridge` tip (note 1).
- [ ] Still open from report 02: the `MatchingSolver` default `max_cycle_len`.
