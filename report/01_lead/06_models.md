# Report 06 (Lead): models.py implemented and unit-tested (L1.2)

**Date:** 2026-11-09
**Owner:** Lead
**Status:** Done locally on `p1/lead`, not yet committed

## 1. What was asked

Implement `donorbridge/models.py` exactly as in the contract, plus `tests/unit/test_models.py`:

- `Pool.__post_init__` checks that ids are unique, and that every edge (i, j) has i != j with both
  ids in the pool. It raises `ValueError` otherwise. It builds a private id -> Family dict.
- `Pool.ids()` is sorted. `subpool(ids)` returns the induced sub-pool. `without_edges(drop)` returns
  a new pool. Neither changes `self`.
- JSON format: `{"name", "families": [... enums as .value], "edges": [[i, j], ...] sorted}`.
  `from_dict` ignores unknown top-level keys.
- `Cycle.of` rejects fewer than 2 families or a repeated id, then rotates so the smallest id comes
  first, keeping the direction. `__post_init__` enforces the canonical form.
- `Solution.validate` rejects rings that are too long or too short, missing edges, a family used
  twice and unknown ids. Each message names the offending ring or family.
- Tests cover: JSON round trip, `subpool` and `without_edges`, canonical rotation, each way
  `validate` can fail, and the empty pool.

## 2. What was done

| File | Change |
| --- | --- |
| `donorbridge/models.py` | Every stub body filled in. No signature, field or public name changed. |
| `tests/unit/test_models.py` | New: 40 tests, 0.12 s. |

How it works:

- **`Pool.__post_init__`** builds `_by_id` and checks the ids and edges in a single pass. It stores
  `_by_id` with `object.__setattr__`. `_by_id` is not a dataclass field, so it plays no part in
  `==` or hashing. Pickling copies it along with the instance's other attributes, which is safe for
  the parallel workers in `run_grid`.
- **`family(fid)`** looks the id up in `_by_id`, so it is O(1) and never uses an id as an index.
- **`subpool`** keeps families in the pool's original order and keeps only the edges with both ends
  inside.
- **`without_edges`** returns `self.edges - frozenset(drop)`.
- **JSON** goes through two private helpers, `_family_to_dict` and `_family_from_dict`. Every key is
  written out explicitly. `from_dict` casts values to `int`/`float` and defaults `region` to 0.
  `save_json` writes indented JSON with a trailing newline.
- **`Cycle`:** a private helper `_check_ring` checks length ≥ 2 and no repeated ids. Both `Cycle.of`
  and `__post_init__` use it, so a direct `Cycle((2, 1))` is rejected too.
- **`Solution.validate`** checks each ring in this order:
  1. Length must be in 2..max.
  2. Every id must be in the pool.
  3. Every edge must be in the pool.
  4. No family may already be in an earlier ring.

  It stops at the first problem. Example messages:
  - `ring (3, 12, 7) has 3 families; allowed 2..2`
  - `ring (3, 99) uses family 99, which is not in pool 'pool_8'`
  - `ring (1, 3) needs edge 3 -> 1, which is not in the pool`
  - `family 3 is in two rings: (3, 12) and (3, 12, 7)`

Verification:

```bash
uv run pytest tests/unit/test_models.py -q                    # 40 passed
uv run pytest tests/integration/test_phase1.py -k lead -rs    # 5 passed, 1 skipped (crossover: scoring stub, L1.3)
uv run pytest tests/unit tests/integration -q -rs             # 48 passed, 15 skipped, 0 failed
```

The fixture-based integration tests now run past `Pool.load_json`. All 15 remaining skips name the
stub they are waiting on:

- `Lead, P1`: 6 tests, waiting on scoring and the solver base (L1.3/L1.4).
- `Generator, P1`: 6 tests.
- `Matching, P1`: 2 tests.
- `Simulation, P1`: 1 test.

## 3. Deviations from the request or the contract

1. **A non-canonical `Cycle` raises `ValueError`, not `AssertionError`.** The request said
   `__post_init__` "asserts" the canonical form. A bare `assert` disappears under `python -O`, so
   this uses an explicit raise. It is the same exception type as `Cycle.of`'s other checks. You
   agreed to this before coding.
2. **`subpool` raises `ValueError` on ids that are not in the pool.** The contract doesn't say what
   should happen. Raising was your choice, so caller bugs (in `resolve.py`, `regions.py`) show up
   straight away.
3. **`family(fid)` raises `KeyError` with a readable message** (`no family with id 0 in pool
   'x'`) instead of the bare dict key. It is still a `KeyError`, as the docstring says.
4. **`validate` checks unknown ids before edges.** That way `(3, 99)` is reported as "family 99 is
   not in the pool" rather than as a missing edge. The request did not set an order.
5. **Two private module helpers** (`_family_to_dict`/`_family_from_dict`, `_check_ring`) and a
   `Pool.__post_init__`/`Cycle.__post_init__`. These add no public names, so the contract is
   unchanged.

## 4. Things to note

1. **No type coercion on construction.** `Pool` does not convert `edges` to a frozenset. If a
   caller passes a plain `set`, `==` still works but `hash(pool)` fails. The generator and
   graph owners should build `frozenset(...)` as the contract says. `from_dict` already does.
2. **`Pool ==` depends on family order and on `name`.** Two pools with the same families in a
   different order are not equal. `to_dict` and `from_dict` keep the order, so round trips are
   exact. Generators must produce families in a deterministic order (as report 05 already says
   about names).
3. **`subpool(ids)` names the new pool `""` unless a name is passed**, following the contract
   default. `regions.py` should pass `f"{pool.name}-r{k}"`, as its docstring says.
   `without_edges` keeps the original name.
4. **The "ring shorter than 2" check in `validate` can't be reached normally**, because `Cycle`
   refuses to build one. The test gets around `__post_init__` to prove the check still works.
5. **`pool_8.to_dict()` matches `tests/fixtures/pool_8.json` key for key.** So a pool saved with
   `save_json` uses the same format as the hand-written fixtures.
6. **No validation of `Family` fields** (PRA in 0..1, region in 0..3). This was not requested, and
   adding it could break the generator's edge cases. Raise it with the generator owner if needed.

## 5. Next steps

- [ ] Review the diff, then commit on `p1/lead`, e.g. `P1 lead: implement models.py (L1.2)`.
      Your unstaged edit to `team/01_lead.md` was left alone. Commit it separately or leave it out.
- [ ] L1.3 `survival.py` + `scoring.py`. This clears the crossover skip.
- [ ] L1.4 `solvers/base.py` + registry. Then open the L1.2–L1.4 PR (target: Wed noon).
- [ ] Add an `ai_logs/lead.md` entry for L1.2. The folder still doesn't exist.
- [ ] Tell the team that `models.py` is real once it is merged. Point out notes 1–3 (frozenset
      edges, deterministic family order, `subpool` naming and unknown-id error).
