# Report 04 (Lead): test fixtures (L1.5)

**Date:** 2026-11-03
**Owner:** Lead
**Status:** Done and checked (by hand and by an independent brute force). Not yet committed.

## 1. What was asked

1. `tests/fixtures/pool_8.json`: the 8-family pool, in our Pool JSON format.
2. Every ring of length 2 and 3 in canonical form (smallest id first, direction kept), with the
   derivation.
3. The optimum transplants for L=2 and L=3, plus one optimal set for each.
4. `tests/fixtures/pool_8.expected.json` = `{"rings_L2", "rings_L3", "opt_L2", "opt_L3"}`.
5. `ring_vs_swap.json`, `greedy_trap.json`, `empty.json`, `no_edges.json` from the section-5 table
   (`team/01_lead.md`), with every edge ABO-compatible.

There was no week-1 paper table: the team never did that exercise. With the user's go-ahead,
`pool_8` was therefore **designed** to test the things that matter, not copied from paper.

## 2. What was done

All files follow the format in `team/01_lead.md` L1.1:
`{"name", "families": [all Family fields, enums as values], "edges": [[i, j], ...] sorted}`.

### 2.1 pool_8

| id | patient / donor blood | patient / donor sex | relation | PRA | note |
|---|---|---|---|---|---|
| 1 | O / A | F / M | spouse | 0.92 | highly sensitised; **in no ring** |
| 3 | A / B | M / F | spouse | 0.15 | |
| 5 | B / O | F / F | other | 0.60 | ABO-compatible with own donor → positive crossmatch |
| 7 | A / A | F / M | spouse | 0.70 | ABO-compatible with own donor → positive crossmatch |
| 9 | A / B | M / M | other | 0.05 | |
| 12 | B / A | M / F | other | 0.25 | |
| 14 | B / A | F / M | other | 0.40 | |
| 21 | A / B | M / F | spouse | **0.80** | highly sensitised, exactly on the `>= 0.80` boundary |

All families are in region 0. There are 4 female and 4 male patients.

**Edges (13).** As successor lists:

| from | 1 | 3 | 5 | 7 | 9 | 12 | 14 | 21 |
|---|---|---|---|---|---|---|---|---|
| to | 3 | 12 | 1, 7, 14 | 3, 21 | 5, 14 | 3, 7 | 9 | 5 |

**Design goals, and where each one shows up:**
- **Ids have gaps** (1, 3, 5, 7, 9, 12, 14, 21): catches any code that uses an id as a list index.
- **Two of the 3-rings do not run in increasing id order**: (3,12,7) and (5,14,9). A cycle finder
  that sorts a ring's families, instead of rotating it, fails here.
- **Longer rings beat swaps**: opt_L3 = 7 > opt_L2 = 4.
- **A greedy trap**: greedy-by-size takes (3,12,7) and (5,14,9) for 6 transplants; the optimum is 7.
- **Overlapping 3-rings**: (3,12,7) and (5,7,21) share family 7, and (5,7,21) and (5,14,9) share
  family 5.
- **A family in no ring**: family 1 has an edge in (5→1) and out (1→3), but every return path is
  longer than 3.
- **A sensitisation story**: family 21 is matched only when rings of 3 are allowed. Family 1 is
  never matched.

**How the blood groups were chosen.** The graph was fixed first. A scratch script then tried all
4⁸ donor-blood assignments; for each one it picked the best patient blood per family. It kept every
edge ABO-compatible and used as few "ABO-compatible but no edge" pairs as possible, since those must
be explained as positive crossmatches. Of the best assignments, this one has the fewest families
that are ABO-compatible with their own donor (2: families 5 and 7).

### 2.2 Rings, found by hand

**2-rings: check every edge for its reverse.** Only 3↔12 and 9↔14 go both ways. Every other edge
has no reverse (e.g. 5→1, but not 1→5).
→ **(3,12), (9,14)**

**3-rings: start from each family s as the smallest id.** Then follow s→a→b→s, using only a, b > s:

| s | paths tried | ring |
|---|---|---|
| 1 | 1→3→12, but 12 does not point to 1 | none |
| 3 | 3→12→7→3 (12→3 just closes the 2-ring) | **(3,12,7)** |
| 5 | 5→7→21→5; 5→14→9→5 (5→1 skipped: 1 < 5) | **(5,7,21), (5,14,9)** |
| 7 | 7→21→5, but 5 < 7 (already counted from s=5) | none |
| 9 | 9→14→9 is the 2-ring; 9→5 skipped | none |
| 12, 14, 21 | every successor is smaller | none |

Starting each ring from its smallest id finds every ring exactly once, already in canonical form.

### 2.3 Optima (count scorer)

- **L=2 → 4**, unique set {(3,12), (9,14)}: the two 2-rings are disjoint, so take both.
- **L=3 → 7**, unique set {(3,12), (9,14), (5,7,21)}:
  1. Family 1 is in no ring, so at most 7 of the 8 families can be matched.
  2. Reaching 7 means matching family 21. Its only ring is (5,7,21), so that ring must be taken.
  3. That uses 5 and 7. So 3 and 12 must come from (3,12), and 9 and 14 from (9,14).

  The bound is reached, and the set is forced at every step.

### 2.4 pool_8.expected.json

```json
{"rings_L2": [[3, 12], [9, 14]],
 "rings_L3": [[3, 12], [9, 14], [3, 12, 7], [5, 7, 21], [5, 14, 9]],
 "opt_L2": 4, "opt_L3": 7}
```

### 2.5 Small fixtures

| Fixture | Families (id: patient/donor blood, PRA) | Edges | Rings |
|---|---|---|---|
| `ring_vs_swap` | 0: A/B 0.10 · 1: B/A 0.20 · 2: A/A 0.85 | 0→1, 1→0, 1→2, 2→0 | (0,1), (0,1,2) |
| `greedy_trap` | 0: A/B 0.50 · 1: B/A 0.10 · 2: A/O 0.90 · 3: B/A 0.60 | 0→1, 0→3, 1→2, 2→0, 2→1, 3→0 | (0,3), (1,2), (0,1,2) |
| `no_edges` | ids 2, 3, 5, 7, 11, all patient O / donor A | none | none |
| `empty` | none | none | none |

I checked these rings by hand against the section-5 table. The crossover numbers also hold: at
p=0.6, swap 2·0.6² = 0.72 vs ring 3·0.6³ = 0.648; at p=0.9, 1.62 vs 2.187.

### 2.6 Verification

These were throwaway scripts in the session scratchpad, not in the repo, and they import no
`donorbridge` code, so they are independent of the team's implementation:
- **Format check on every fixture:** ids unique; edges sorted, unique, with no self-loops and only
  known ids; every edge ABO-compatible.
- **Brute force on `pool_8.json`:**
  - All 2- and 3-permutations of the ids, to find rings.
  - Every subset of rings, to find the optima.
  - It matched §2.2 and §2.3 exactly, including that both optimal sets are unique.
  - It also confirmed greedy = 6.
  - The same check with expected-transplant weights gives the same plan as the L=3 optimum at
    p = 0.6, 0.7 and 0.9.
- `uv run pytest -q` → 3 passed. Nothing loads the fixtures yet, because `Pool.load_json` is a stub.

## 3. Deviations from the request or the contract

1. **`pool_8` is designed, not hand-copied from week 1.** There was no paper table.
   `team/*.md` (section 5) and `Plan.md` (week-1 row) still say "solved by hand in week 1". Those
   files are not mine, so I left them unchanged. Tell the team.
2. **`rings_L3` holds every ring of length ≤ 3, not only the 3-rings.** That way it equals
   `find_cycles(pool_8, 3)` directly, sorted by (len, families), which is what
   `test_p1_matching_rings_on_fixtures` compares. To get only the 3-rings, filter by `len == 3`.
3. **Rings are stored as plain lists**, e.g. `[3, 12, 7]`. Compare them as
   `[list(c.families) for c in rings]`.
4. **`no_edges` uses ids 2, 3, 5, 7, 11**, not 0..4 (section 5 only says "5 families"), to catch
   index bugs.
5. **No extra keys in the expected file** (e.g. the optimal sets). The schema was given; the sets
   are in §2.3 above.
6. No contract change.

## 4. Things to note

1. **Missing edges can be ABO-compatible.** They stand for positive crossmatches (e.g. 12→21 and
   1→21 in `pool_8`, and 1→0 in `greedy_trap`). So a test that rebuilds edges from blood groups
   alone will **not** reproduce any fixture.
2. **`pool_8` has a second greedy trap** (greedy 6 vs optimum 7). It is handy for
   `test_p2_heuristics_local_search_fixes_trap`.
3. **Family 21's PRA is exactly 0.8**, so `highly_sensitised` must use `>=`, not `>`.
4. **Ideas for the simulation test** on the L=3 optimum:
   - transplants = 7;
   - highly sensitised patients matched 1 of 2 (21 yes, 1 no);
   - female patients matched 3 of 4 (5, 7, 14);
   - male patients matched 4 of 4.
5. **Please re-check §2.2 and §2.3 by hand once** (about 15 minutes). It is good viva preparation.

## 5. Next steps

- [ ] Commit and push the fixtures and this report.
- [ ] Tell the team that `pool_8` was designed rather than hand-solved, and that `rings_L3`
      includes the 2-rings.
- [ ] L1.7 `tests/integration/test_phase1.py`, using the `pool_8` answers above.
- [ ] Once `Pool.to_dict` and `from_dict` exist, run the JSON round-trip on every fixture.
