# Design · Lead

Owner: Lead · Last updated: 2026-11-09

## 1. The ILP formulation (L2.1, planned)

`solvers/ilp.py` is still a P2 stub, so this section is the formulation I will implement, in Plan.md's notation.

Let $\mathcal{C}_L$ be every ring of length $2..L$ (from `find_cycles`). One 0/1 variable $x_c$ per ring: $x_c = 1$ means ring $c$ goes ahead.

$$
\max \sum_{c \in \mathcal{C}_L} w_c \, x_c \quad \text{s.t.} \quad \sum_{c \ni v} x_c \le 1 \;\; \text{for every family } v, \qquad x_c \in \{0, 1\}
$$

- **Objective:** total weight of the chosen rings.
- **One constraint per family:** each family is in at most one chosen ring. It is "≤ 1", not "= 1", because a family may stay unmatched until the next round.
- **Weights plug in from the scorer.** The ILP reads $w_c$ from `self.weights(pool, cycles)`, so it never knows which scorer it has:
  - `CountScorer`: $w_c = |c|$.
  - `ExpectedTransplantScorer(p)`: $w_c = |c|\,p^{|c|}$. In general, $w_c = |c| \prod_{e \in c} s_e$, where $s_e$ is `survival.edge` for the edge $e$.
  - So a 3-ring beats a 2-swap on the same families iff $3p^3 > 2p^2 \iff p > 2/3$. At exactly $2/3$ the two tie at $8/9$.
- **Why L = 2 is easy:**
  - A 2-ring is a mutual pair $i \leftrightarrow j$.
  - Choosing disjoint 2-rings is choosing a matching in the undirected graph of mutual pairs.
  - That is solvable in polynomial time (augmenting paths or Edmonds' blossom). This is the Matching owner's `MatchingSolver`.
- **Why L = 3 is hard:**
  - A 3-ring covers 3 families at once, so choosing disjoint rings becomes set packing with sets of size ≤ 3.
  - Abraham, Blum and Sandholm (2007) reduce 3-dimensional matching to it, so it is NP-hard.
  - This is why we use an ILP (exact, worst case exponential) plus hand-written heuristics and branch and bound.

## 2. The Solver template method (`solvers/base.py`)

`Solver.solve(pool, cycles=None)` does these six steps, in this order, for every solver:

1. **Find rings:** if `cycles is None`, call `find_cycles(pool, self.max_cycle_len)`. It is imported inside the method.
2. **Filter:** keep rings with `len(c) <= self.max_cycle_len`. This builds a new list, so the caller's list is untouched.
3. **Time the hook:** `chosen, optimal, stats = self._solve(pool, cycles)`, timed with `time.perf_counter()`. Ring enumeration is not included.
4. **Optimal flag:** if `not self.exact`, set `optimal = False`.
5. **Build the Solution:** rings sorted by `(len, families)`, `objective = self.scorer.total(chosen, pool)`, plus runtime, optimal and stats.
6. **Validate:** `solution.validate(pool, self.max_cycle_len)` raises `InvalidSolutionError` on a bad plan. Then return the Solution.

`__init__` raises `ValueError` if `max_cycle_len` is not in the subclass's `supported_lengths`. The scorer defaults to a fresh `CountScorer()`.

**Why this is the Template Method pattern:**
1. `solve` fixes the skeleton of every solve once, in the base class.
2. The one step that varies, choosing the rings, is the abstract hook `_solve`, which each subclass overrides.
3. So all seven solvers share the same timing, scoring, optimal-flag and validation logic. Results are comparable, and an invalid plan can never be returned.

**What a subclass must do:**
- Set `name`, `exact` and (if not `(2, 3, 4)`) `supported_lengths`.
- Implement `_solve(pool, cycles) -> (list[Cycle], bool | None, dict)`.
- Rank rings by `self.weights(pool, cycles)`, never by `len(c)`.
- Never override `solve`.

## 3. Why the Scorer is passed in (Strategy)

The weight rule is an object (`Scorer`) passed to the solver, not a flag inside it:
- **One place to get it right.** The weight rules live in `scoring.py` (and P3 `fairness.py`), not in seven copies of `if mode == ...`.
- **No extra solver code.** Failure-awareness is a constructor argument: `get_solver("greedy", scorer=ExpectedTransplantScorer(0.7))`. A new scorer (e.g. `FairnessScorer`) changes no solver.
- **One audit.** L3.3 only checks that each `_solve` uses `self.weights`.

## 4. The stub-skip hook and `--gate` (`tests/conftest.py`)

1. pytest builds a report for each phase (setup, call, teardown); our `pytest_runtest_makereport` wrapper receives it from `yield`.
2. If the test body (`call`) failed with `NotImplementedError` and `--gate` is off, we relabel it `skipped` with reason `stub: <owner>, P<n>`.
3. With `--gate`, or for any other exception or phase, the report is returned unchanged, so unfinished stubs fail the gate.

## 5. Merge order, P1–P3 (who depends on whom)

Read from the architecture diagram: Pool → graph → rings → Solver(+Scorer) → Solution → simulation → grid.

- **P1:** Lead core (`models`, `survival`, `scoring`, `solvers/base`, merged) → Generator and Matching in parallel → Heuristics (their tests call `solve` without rings, so they need `find_cycles`) and Simulation (its analytic test runs greedy) → e2e.
- **P2:** Lead ILP first (brute-force, heuristics-≤-ILP and B&B v1 tests compare against it); Glasgow loader → kep oracle; `run_grid` needs generator, `find_cycles` and solvers; `resolve` needs a solver and `FailureSimulator`.
- **P3:** `crosscheck` needs every solver; `SensitisationSurvival` and `FairnessScorer` before the grid-features test.

## 6. Open contract decisions

1. **`MatchingSolver` and `max_cycle_len`** (reports 02 §4.1, 08 §4.1). The base default is 3 but `MatchingSolver.supported_lengths = (2,)`, so `get_solver("matching")` raises `ValueError` unless given `max_cycle_len=2`. `run_grid` always passes `max_len`, and `team/03_matching.md` already expects `ValueError` at L=3. Keep and document it, or give `MatchingSolver` a default of 2 (then update `test_get_solver_checks_max_cycle_len`).
2. **`PoolMetrics` is unhashable** (frozen, but has dict fields); harmless unless put in a set (report 02, §4.2).
3. **`Family` fields are not validated** (PRA in 0..1, region in 0..3); ask the Generator owner (report 06, §4.6).
4. **Allowed libraries** omit `nbformat` (dev) and `kep_solver` (oracle extra, only under `oracle/`) (report 01, §4.3).

## 7. Mismatches (code vs playbook / Plan.md; reported, not resolved)

1. Playbook §1 says green PRs merge "in any order" because files never overlap. That is true for git, but the integration tests go green only in the dependency order of section 5.
2. The contract comment on `Solver.solve` (playbook §6) lists find, filter, time, score, build, validate. It omits "force `optimal=False` if not exact", which the L1.4 prompt and the code both do.
3. Plan.md ("What we'll have") says "five solvers"; the registry has seven.
4. Plan.md and every team file's §5 say `pool_8` was "solved by hand in week 1"; it was designed and brute-force checked (report 04).
5. The L1.2 prompt says `Cycle.__post_init__` "asserts" the canonical form; the code raises `ValueError` (report 06, §3.1).
6. Playbook §7 asks for this file by 2 Nov; it lands on 9 Nov. Section 1 describes the plan, because `ilp.py` is still a stub.
