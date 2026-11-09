# 02 · Design file (design gate, H0)

Date: 2026-11-09

## What was asked

The design-gate item from section 7 of the playbook: `docs/design/heuristics.md` with dated pseudocode and flowcharts for first-come, greedy, local search, and branch and bound v1 and v2, plus hand traces on `greedy_trap` and `pool_8` and a list of unit tests. The gate was due Mon 2 Nov. The heuristics owner asked the AI to write the file on 2026-11-09.

## What was done

Filled every section of the lead's template (Modules, Pseudocode, Flowchart, Unit-test cases, Decisions) and added a Hand traces section:
- **Pseudocode** for all four solvers. B&B v2 includes its branching rule, the bookkeeping that makes undo cheap, a completeness argument and a proof that the bound is valid (H3.1).
- **Mermaid flowcharts** for first-come and greedy, local search, and B&B v2.
- **Hand traces** on `greedy_trap`, `pool_8` and `ring_vs_swap`. Every number was checked against the study implementation, including the node and prune counts: v1 on the trap has 7 nodes and 2 prunes; v2 from greedy's 3 has 5 nodes and 1 prune.

## Deviations and things to note

- **Dated 2026-11-09, not 2 Nov.** That's the day it was written; the date was not backdated.
- **pool_8 is now the local-search "stuck" example,** in place of a made-up pool. Under count weights, greedy and local search get 6 and the optimum is 7, because the fix needs both 3-rings taken out at once.
- **The v3 "family price" bound is described as planned and untested.** The playbook fixes the v2 bound, so adding v3 needs measuring and a word with the lead (Decision 8).
- **v1's exclude branch is a loop, not a recursive call.** One call per ring would pass Python's recursion limit on pools of around 100 or more.

## Next steps

- P2: `local_search.py`, then B&B v1, following this file.
- Measure v3 against v2 on pools of 30–100 before the P3 gate on 16 Nov.
