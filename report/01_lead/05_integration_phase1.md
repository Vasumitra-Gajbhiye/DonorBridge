# Report 05 (Lead): Phase 1 integration tests (L1.7)

**Date:** 2026-11-03
**Owner:** Lead
**Status:** Done locally and verified. Not yet committed.

## 1. What was asked

1. Write `tests/integration/test_phase1.py` from the "Integration test spec: Phase 1" list.
2. Use `load_fixture(name) -> Pool` from `tests/conftest.py` ("write that too").
3. Every test name starts with `test_p1_<role>_` or `test_p1_e2e_`, so `-k <role>` works.
4. The whole file runs in under 30 s. Use `pytest.approx` for floats and fixed seeds for randomness.

## 2. What was done

| File | Contents |
|---|---|
| `tests/integration/test_phase1.py` | The 20 tests from the spec table, one function each, in the same order. Also four small helpers: `rings_as_lists`, `hand_solution`, `india_pools` and `check_heuristic_plan`. |

**Tests per role** (`uv run pytest tests/integration/test_phase1.py -k <role> -rs`):

| `-k` | Tests |
|---|---|
| `lead` | all_modules_import, registry_has_seven_solvers, pool_json_roundtrip, cycle_canonical_form, validate_rejects_bad_solutions, expected_weights_crossover |
| `generator` | deterministic, pool_shape, selection_effect, report_consistent |
| `matching` | graph_matches_edges, rings_on_fixtures, dfs_equals_nested_loops |
| `heuristics` | first_come_valid, greedy_on_fixtures |
| `simulation` | metrics_on_fixture, failure_p1_exact, failure_matches_analytic |
| `e2e` | pipeline_india_100, solver_names_resolve |

**Verification**

1. **Real repo, mostly stubs:**
   - `uv run pytest tests/integration -q -rs -m "not oracle"` (the CI command) gives **2 passed, 18 skipped**.
   - Skip reasons: 13 × `stub: Lead, P1`, 5 × `stub: Generator, P1`.
   - With `--gate`: 18 failed, 2 passed.
   - `-k generator` selects exactly 4 tests.
   - `uv run pytest tests/unit -q`: 3 passed.
2. **Against a correct implementation:** I wrote a throwaway reference version of every P1 stub in a scratchpad copy of the repo, then deleted it. It never touched the repo, so nobody's "write it yourself" algorithm was written for them.
   - Result: **20 passed with `--gate` in 0.77 s**.
3. **The tests catch real bugs:** I injected one bug at a time into the reference version and checked which tests went red:

| Injected bug | Caught by |
|---|---|
| `Cycle.of` sorts instead of rotating | cycle_canonical_form, rings_on_fixtures, dfs_equals_nested_loops, and 4 more |
| `highly_sensitised` uses `>` not `>=` | simulation_metrics_on_fixture (family 21, PRA exactly 0.80) |
| `expected()` half-width missing the 1.96 | simulation_failure_matches_analytic |
| Simulated mean 5 % too high | failure_p1_exact, failure_matches_analytic, e2e_pipeline |
| Generator ignores the seed | generator_deterministic, generator_report_consistent |
| An edge that is not ABO-compatible | generator_pool_shape |
| `validate` skips the overlap check | lead_validate_rejects_bad_solutions |
| DFS without the "only ids > start" rule (duplicate rings) | rings_on_fixtures, dfs_equals_nested_loops |
| Base class does not force `optimal=False` for heuristics | heuristics_first_come_valid |
| Greedy takes rings in list order, not by weight | heuristics_greedy_on_fixtures |
| Metrics count donor sex instead of patient sex | simulation_metrics_on_fixture |

## 3. Deviations from the request or the contract

1. **The spec was not pasted.** The prompt still contained the placeholder. I used the table in
   `team/01_lead.md` §8 (the same thing I did in report 02).
2. **`load_fixture` was not rewritten.** It already exists in `tests/conftest.py` from L1.6
   (report 03), with `load_expected`. `conftest.py` is unchanged.
3. **One function per spec row, using loops, not `parametrize`.** This keeps the CI skip count
   equal to the number of unfinished checks in the spec, which makes it a readable progress board.
   Assertion messages name the fixture, seed or id that failed.
4. **Extra assertions beyond the spec.** Each is cheap and either restates the contract or stops a
   check from passing for the wrong reason:
   - `validate_rejects_bad_solutions` first checks that a **valid** plan (the pool_8 L=3 optimum)
     passes. Otherwise a `validate` that always raises would pass the test.
   - `generator_deterministic` also uses a fresh generator. Its "different seed" check compares
     `(families, edges)`, not the whole pool, because a seed in the pool name would make any two pools differ.
   - `generator_report_consistent` also checks `generate(n, s) == generate_with_report(n, s)[0]`
     (the contract defines `generate` that way).
   - `pool_json_roundtrip` also round-trips through `json.dumps`/`json.loads`, so `to_dict` must
     really be JSON-ready.
   - `expected_weights_crossover` also checks exact weights `2p²` and `3p³`, the tie at p = 2/3, and
     that `ExpectedTransplantScorer(UniformSurvival(0.6))` equals `ExpectedTransplantScorer(0.6)`.
   - `rings_on_fixtures` and `greedy_on_fixtures` also cover `empty` and `no_edges` (section 5 says
     every solver returns 0 rings on them).
   - `dfs_equals_nested_loops` asserts at least one ring was found, so the check cannot pass
     vacuously.
   - `failure_p1_exact` also checks that `expected()` returns (7.0, 0.0).
   - `failure_matches_analytic` also checks the reported half-width ≈ 1.96·SE (rel 10 %). The
     simulation playbook (S1.2) specifies that formula.
   - `metrics_on_fixture` also checks `by_blood`, `rings_by_len` and `expected_transplants` at p = 0.5.
   - `e2e_pipeline_india_100` checks the modules agree: metrics vs plan, metrics vs
     `ExpectedTransplantScorer`, simulated mean within 4 SE, and every chosen ring is one of the
     rings passed in.
5. **The standard error in `failure_matches_analytic` is computed from the formula**
   (Var = Σ |c|² q(1−q), with q = p^|c|), not taken from the simulator's own half-width. If it came
   from the simulator, an inflated half-width would make the test pass trivially.
6. **"A greedy solution" is greedy on `pool_8`** (two 3-rings, 2.058 expected at p = 0.7). The spec
   does not name a pool, and this keeps the generator out of a simulation test.
7. **`e2e_solver_names_resolve` passes a supported `max_cycle_len`** (3, or 2 for `matching`). The
   open question from report 02 (`get_solver("matching")` with the default 3 raises `ValueError`) is
   therefore **not decided by this test**: it passes whichever way you decide. No contract change.

## 4. Things to note

1. **Most tests wait for your models.py.** Every fixture-based test calls `Pool.load_json`, so 13 of
   the 18 skips say `stub: Lead, P1`. A teammate whose code is finished still sees a skip until
   L1.2 lands. **Your Wed-noon merge of L1.2–L1.4 unblocks the board.** Until then, teammates should
   rely on their unit tests.
2. **Tests that need more than one owner.** These go green only when every listed owner is done:

   | Test | Needs |
   |---|---|
   | `first_come_valid` | heuristics + matching (`solve` calls `find_cycles`) + generator (its 10 random pools run after the fixtures) |
   | `greedy_on_fixtures` | heuristics + matching |
   | `failure_matches_analytic` | simulation + heuristics + matching |
   | `e2e_*` | everyone |

   The simulation metrics and p = 1 tests use hand-built plans, so they need only Lead code plus
   simulation.
3. **What the tests assume beyond the signatures.** These follow the agreed shapes in each
   playbook; tell the owners:
   - `FailureOutcome.went_ahead` and `.cancelled` are **tuples**, and `went_ahead` keeps the plan's
     ring order.
   - `PoolMetrics.by_blood` is keyed by the blood-group value (`"O"`). Enum keys also work, because
     `BloodGroup` is a `str` enum.
   - Zero entries in `rings_by_len` are ignored.
   - `Solution.solver` equals the registry name.
   - Pool names must be deterministic, since `Pool ==` compares `name`.
4. **Fixed seeds make the statistical tests deterministic.** With `SEED = 2026`, a correct simulator
   still has about a 0.3 % chance of landing outside 3 SE in `failure_matches_analytic`. If that
   ever happens: check the formula first, and only then change the seed. The e2e test uses 4 SE.
5. **Timing:** 0.77 s against the reference version. Slower real code still has plenty of room
   under 30 s, and the e2e test has its own 10 s check.
6. **CI will now find tests to collect** in the integration step (report 03, note 6), so both test
   steps should be green.

## 5. Next steps

- [ ] Commit `tests/integration/test_phase1.py` and this report, and push to `main` (playbook step 1:
      the phase test file goes straight to `main`).
- [ ] Post in the group chat with each role's `-k` command. Point out that skips reading
      `stub: Lead, P1` are waiting on you, not on them.
- [ ] L1.2–L1.4 on `p1/lead`, PR by Wed noon. That unblocks 13 of the 18 skips.
- [ ] Still open from report 02: the `MatchingSolver` default `max_cycle_len`.
- [ ] Add an `ai_logs/lead.md` entry for L1.7. The `ai_logs/` folder from L1.1 does not exist yet.
