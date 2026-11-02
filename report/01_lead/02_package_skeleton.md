# Report 02 (Lead): Package skeleton, the contract commit (L1.1)

**Date:** 2026-11-03
**Owner:** Lead
**Status:** Done locally and verified. Not yet committed.

## 1. What was asked

Generate the full `donorbridge/` skeleton from the module map, so that five people can work in
parallel without editing the same file:

- Every module gets a docstring with its purpose, owner and phase.
- Every public name gets its contract signature, a docstring, and the body
  `raise NotImplementedError("<owner>, P<n>")`.
- The contract dataclasses (`models.py`, `Setting`, `GridSpec`, `ROW_COLUMNS`) are written in full.
- Solver subclasses set their ClassVars.
- The registry, `EXPERIMENTS`, the stub CLI and the re-exporting `__init__.py` files are written.
- At the end, a one-line command that imports everything.

## 2. What was done

46 modules were created under `donorbridge/`:

| Package | Files (owner, phase) |
|---|---|
| core | `models.py`, `survival.py`, `scoring.py` (Lead, P1); `compatibility.py` (Generator, P1); `graph.py`, `cycles.py` (Matching, P1); `__main__.py` (Lead) |
| `solvers/` | `base.py` (Lead, P1); `ilp.py` (Lead, P2); `first_come.py`, `greedy.py` (Heuristics, P1); `local_search.py`, `branch_bound.py` (Heuristics, P2); `brute_force.py` (Matching, P2); `matching.py` (Matching, P3) |
| `generator/` | `calibration.py`, `saidman.py` (P1); `report.py` (P2); `survival_models.py`, `regions.py` (P3). All Generator. |
| `simulation/` | `metrics.py`, `failure.py` (P1); `resolve.py` (P2); `fairness.py` (P3); `plots.py` (P4). All Simulation. |
| `experiments/` | `grid.py`, `survival_sweep.py` (Simulation, P2); `fairness.py`, `runtime.py` (Simulation, P4); `blood_mix.py`, `female_sensitisation.py`, `regions.py` (Generator, P4); `cycle_growth.py` (Matching, P4); `optimality_gap.py`, `ring_length.py` (Heuristics, P4); `answer.py` (Lead, P4) |
| `oracle/` | `glasgow.py`, `kep_oracle.py` (P2); `crosscheck.py` (P3). All Lead. |
| `demos/` | `scripts.py` (Matching, P4) |

Real code was written, rather than stubs, only for these:

- `get_solver`, which raises `KeyError` and lists the valid names;
- the `SOLVERS`, `EXPERIMENTS` and `DEMOS` dicts;
- the CLI, which prints `not implemented yet (P<n>)` and exits with code 2;
- the `__init__.py` re-exports.

**Verification**

The one-line import command:

```bash
uv run python -c "import pkgutil, importlib, donorbridge as d; m=[x.name for x in pkgutil.walk_packages(d.__path__, 'donorbridge.')]; [importlib.import_module(x) for x in m]; print(len(m), 'modules OK')"
```

It printed `46 modules OK`. Other checks that passed:

- `SOLVERS` has the seven names in contract order. `matching` has `exact=True` and
  `supported_lengths=(2,)`. Brute force, branch and bound, and the ILP are exact. The three
  heuristics are not.
- `get_solver("x")` raises a `KeyError` that lists the valid names.
- `get_solver("greedy")` raises `NotImplementedError: Lead, P1`. This is expected until
  `Solver.__init__` exists.
- `EXPERIMENTS` has all nine experiment names.
- `python -m donorbridge run` prints `not implemented yet (P2)` and exits with code 2.
  `demo` prints `(P4)` and also exits with code 2.
- An AST scan found that every module docstring has `Owner:` and `Implemented in:`, and that every
  public class and function has a docstring.

## 3. Deviations from the request or the contract

1. **The module map was not pasted.** The prompt still contained the placeholder. I used the table
   in `team/01_lead.md` §5, which is identical in every playbook.
2. **Agreed shapes written as fields.** `Calibration`, `GenerationReport`, `PoolMetrics` and
   `FailureOutcome` were not on the list of "write the fields now". I wrote their fields anyway,
   using the "Agreed shapes" in the generator and simulation playbooks, so that teammates start from
   the agreed names. Their methods and properties are still stubs.
3. **`INDIA` and `US` are placeholders.** They must exist at import time, because
   `SaidmanGenerator(calibration=INDIA)` uses `INDIA` as a default argument. I set them to
   `Calibration(name=..., blood_freq=(), pra_bands=(), shares=NaN)`. NaN and empty values make any
   accidental use fail loudly, instead of producing plausible but fake numbers. The Generator owner
   replaces them in G1.1.
4. **`CountScorer.name = "count"` is set now.** It is a class constant, already specified in L1.3.
   `ExpectedTransplantScorer` sets its name in `__init__`, which is still a stub.
5. **The top-level `donorbridge/__init__.py` re-exports only the core modules.** These are models,
   survival, scoring, compatibility, graph and cycles. It does not re-export the subpackages. This
   keeps `import donorbridge` light (no pandas or pulp) and avoids import cycles. Each subpackage
   re-exports its own names.
6. **One phase per stub for modules that span two phases.** For modules marked P1–P2 or P2–P3 in the
   map, each stub names the phase in which its task first appears:
   - `calibration.py` and `saidman.py`: P1;
   - `ilp.py`, `branch_bound.py`, `grid.py` and `survival_sweep.py`: P2.
7. **CLI phases.** The phases come from the lead tasks:
   - `run`: P2 (L2.4);
   - `bench`: P3 (L3.1);
   - `sweep`, `results` and `demo`: P4 (L4.1 and L4.3).
8. **`from __future__ import annotations` in every module.** `pd.DataFrame` and `nx.DiGraph` are
   imported under `TYPE_CHECKING` only. Signatures are unchanged.

## 4. Things to note

1. **Contract issue (flagged, not changed): `get_solver("matching")` will fail with the default
   arguments.** `Solver.__init__` defaults to `max_cycle_len=3`, but `MatchingSolver` supports only
   `(2,)`. Once L1.4 adds the `ValueError` check, `get_solver("matching")` raises. Callers must pass
   `max_cycle_len=2`. This matters for the integration test `test_p1_e2e_solver_names_resolve` and
   for `crosscheck`. `run_grid` is fine, because it always passes `max_len`. You need to decide:
   either keep the contract and document it, or give `MatchingSolver` its own default of 2.
2. **`PoolMetrics` is unhashable.** It is frozen but has `dict` fields, so `hash()` raises
   `TypeError`. That is harmless unless someone puts it in a set. `Solution.stats` is safe because
   it is declared with `compare=False`.
3. **Teammates must not add modules under `donorbridge/`.** Every file in the map now exists.
4. **Not part of this prompt, but listed under L1.1:**
   - `ai_logs/<role>.md` ×5;
   - `docs/design/<role>.md` ×5;
   - `notebooks/demo.ipynb` (owned by Matching). This is not a Python module, so I did not create
     it.
5. **CI is still red.** `tests/unit/` and `tests/integration/` do not exist yet (see report 01).
   That is L1.5 and L1.6.

## 5. Next steps

- [ ] Decide on the `MatchingSolver` default `max_cycle_len` (note 1).
- [ ] Create empty `ai_logs/<role>.md` and `docs/design/<role>.md` headers (the rest of L1.1).
- [ ] L1.5 fixtures and L1.6 `tests/conftest.py`, so that CI goes green. Then commit everything
      directly to `main` (Phase 0) and post in the group chat.
- [ ] L1.2–L1.4: implement models, survival, scoring and the Solver base on `p1/lead`.
