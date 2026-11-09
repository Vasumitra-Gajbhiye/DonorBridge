# AI log · Lead

Owner: Lead

<!--
Add one entry per AI prompt, newest last, in this format (team/01_lead.md, section 3).
Mark the mode: 🧑‍🏫 tutor mode (your stage algorithm) or 🛠 builder mode (plumbing).

### YYYY-MM-DD · <prompt id> · <short title> · <mode>
- Tool: Claude / ChatGPT / Copilot
- Prompt: <prompt id> as written (or what you changed)
- Kept: what you used from the answer
- Corrected: what the AI got wrong, and how you caught it (a failing test, the paper, a teammate)
- Time: roughly how much it saved or cost
-->

### 2026-11-03 · L1.0 · Repo tooling as a uv project · 🛠 builder mode
- Tool: TODO (lead): fill in
- Prompt: L1.0 as written.
- Kept: `pyproject.toml` (numpy, pandas, matplotlib, networkx>=3.1, pulp==2.9.0, highspy; dev group pytest + nbformat; `oracle` extra kep_solver; `slow`/`oracle` markers), `.python-version`, `uv.lock` (35 packages, kep_solver 4.0.2 locks next to pulp 2.9.0), exported `requirements.txt`, `.gitignore`, `.github/workflows/ci.yml` (report 01, §2).
- Corrected: the prompt's CI check (export to a temp file and diff it) would always fail, because `uv export` writes its own `-o <path>` into the file header. CI now re-exports in place and fails on `git diff --exit-code -- requirements.txt` (report 01, §3.1). Report 01 §4.3 also notes that nbformat and kep_solver are missing from the team's allowed-library list.
- Time: TODO (lead): fill in

### 2026-11-03 · L1.1 · Package skeleton (the contract commit) · 🛠 builder mode
- Tool: TODO (lead): fill in
- Prompt: L1.1, but the module-map placeholder was not pasted; the AI used the table in team/01_lead.md §5 instead (report 02, §3.1).
- Kept: 46 stub modules with owner/phase docstrings and contract signatures; real code only for `get_solver`, the `SOLVERS`/`EXPERIMENTS`/`DEMOS` dicts, the stub CLI (exit code 2) and the `__init__.py` re-exports (report 02, §2).
- Corrected: `INDIA`/`US` are NaN/empty placeholders so accidental use fails loudly; the agreed-shape fields of `Calibration`, `GenerationReport`, `PoolMetrics`, `FailureOutcome` were written although not asked for; the top-level `__init__.py` re-exports only core modules (report 02, §3.2, 3.3, 3.5). Flagged, not changed: `get_solver("matching")` fails with the default `max_cycle_len=3` (report 02, §4.1).
- Time: TODO (lead): fill in

### 2026-11-03 · L1.5 · Test fixtures · 🛠 builder mode
- Tool: TODO (lead): fill in
- Prompt: L1.5, without the week-1 paper table (the exercise was never done); with my go-ahead `pool_8` was designed instead (report 04, §1).
- Kept: `pool_8.json` (ids with gaps, rings not in id order, greedy trap 6 vs 7), `pool_8.expected.json` (opt_L2 = 4, opt_L3 = 7), `ring_vs_swap`, `greedy_trap`, `empty`, `no_edges` (report 04, §2).
- Corrected: no paper answer existed to compare against, so no disagreement was recorded; the rings and optima were re-derived by hand and by an independent brute force that imports no donorbridge code. `rings_L3` holds every ring of length ≤ 3, not only the 3-rings, so it equals `find_cycles(pool_8, 3)` (report 04, §2.6, §3.1, §3.2).
- Time: TODO (lead): fill in

### 2026-11-03 · L1.6 · conftest with the stub-skip hook · 🛠 builder mode
- Tool: TODO (lead): fill in
- Prompt: L1.6 as written.
- Kept: `load_fixture`, `load_expected`, `--run-slow`, `--gate`, the `pytest_runtest_makereport` hook and its 3-line explanation, and 3 pytester self-tests in `tests/unit/test_conftest_gate.py` (report 03, §2).
- Corrected: the hook only relabels reports that actually failed, so an xfail test is not turned into a stub skip; an extra self-test covers `--run-slow` (report 03, §3.1, §3.2). The editable install was stale and was fixed with `uv sync --reinstall-package donorbridge` (report 03, §4.1).
- Time: TODO (lead): fill in

### 2026-11-03 · L1.7 · Phase 1 integration tests · 🛠 builder mode
- Tool: TODO (lead): fill in
- Prompt: L1.7, but the spec placeholder was not pasted; the AI used the table in team/01_lead.md §8 (report 05, §3.1).
- Kept: `tests/integration/test_phase1.py`, one function per spec row (20 tests) with `-k <role>` names; checked against a throwaway reference implementation (20 passed with `--gate`) and 11 injected bugs (report 05, §2).
- Corrected: the standard error in `failure_matches_analytic` comes from the formula, not from the simulator's own half-width, so an inflated half-width cannot pass the test; `e2e_solver_names_resolve` passes `max_cycle_len=2` for matching, which leaves the open matching-default decision untouched (report 05, §3.5, §3.7).
- Time: TODO (lead): fill in

### 2026-11-09 · L1.2 · models.py · 🛠 builder mode
- Tool: TODO (lead): fill in
- Prompt: L1.2 as written.
- Kept: every `models.py` stub filled in with no contract change, and `tests/unit/test_models.py` (40 tests) (report 06, §2).
- Corrected: a non-canonical `Cycle` raises `ValueError` instead of the requested `assert`, because asserts disappear under `python -O` (agreed before coding). Also: `subpool` raises `ValueError` on unknown ids, and `validate` checks unknown ids before edges (report 06, §3.1, §3.2, §3.4).
- Time: TODO (lead): fill in

### 2026-11-09 · L1.3 · survival.py and scoring.py · 🛠 builder mode
- Tool: TODO (lead): fill in
- Prompt: L1.3 as written.
- Kept: `UniformSurvival`, `SurvivalModel.cycle`, `CountScorer`, `ExpectedTransplantScorer`, `Scorer.total`, and `tests/unit/test_scoring.py` (27 tests, including the p > 2/3 crossover) (report 07, §2).
- Corrected: p is stored as `float(p)`, so `ExpectedTransplantScorer(1)` is named `expected(p=1.0)` and every spelling of the same p gives one name; `UniformSurvival.p` and `ExpectedTransplantScorer.survival` are public attributes the contract implies (report 07, §3.1, §3.2).
- Time: TODO (lead): fill in

### 2026-11-09 · L1.4 · Solver base and registry · 🛠 builder mode
- Tool: TODO (lead): fill in
- Prompt: L1.4 as written.
- Kept: `Solver.__init__`, the six-step `solve` template method, `weights`, `__repr__`, `tests/unit/test_solver_base.py` (36 tests), and the 3-line Template Method explanation (report 08, §2, §6).
- Corrected: `solvers/__init__.py` was left unchanged because the L1.1 skeleton was already complete (report 08, §3.1). `get_solver("matching")` raises `ValueError` with the default `max_cycle_len=3`, and a unit test now pins that behaviour until the decision is made (report 08, §4.1).
- Time: TODO (lead): fill in
