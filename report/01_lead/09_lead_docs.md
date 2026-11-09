# Report 09 (Lead): AI-log and design headers, lead AI log, lead design file, unblock status

**Date:** 2026-11-09
**Owner:** Lead
**Status:** Done and committed on `p1/lead`, then pushed. The PR is not opened yet (the command is in the chat answer).

## 1. What was asked

1. **The rest of L1.1:**
   - `ai_logs/{lead,generator,matching,heuristics,simulation}.md`, each with a title, an owner line and the section-3 template as a comment;
   - `docs/design/{generator,matching,heuristics,simulation}.md`, each with a title, an owner line and empty headings.
2. **Fill `ai_logs/lead.md`** with one entry per finished task: L1.0, L1.1, L1.5, L1.6, L1.7, L1.2, L1.3, L1.4.
   - Dates come from git log.
   - "Kept" and "Corrected" come only from reports 01–08; any field a report doesn't cover gets `TODO (lead): fill in`.
   - Every entry is marked 🛠 builder mode.
3. **Write `docs/design/lead.md`**, under 2 pages:
   - the ILP;
   - the Solver template method;
   - the Scorer as a strategy;
   - the stub-skip hook;
   - the merge order for P1–P3;
   - open contract decisions;
   - a Mismatches section.
4. **Run the phase-1 tests, group the skips by owner, and draft a group-chat message.** The message goes in the chat answer only and is not committed.
5. **Prove the unit tests still pass, then commit and push** with no AI attribution, and give the `gh pr create` command without running it.
6. **Write this report.**

## 2. What was done

| File | Content |
| --- | --- |
| `ai_logs/{generator,matching,heuristics,simulation}.md` | `# AI log · <Role>`, `Owner: <Role>`, then the section-3 template inside `<!-- -->`, with the mode marker added to the heading line. No entries. |
| `ai_logs/lead.md` | The same header, plus 8 entries in the order you gave. Each one cites the report section it comes from. |
| `docs/design/{generator,matching,heuristics,simulation}.md` | `# Design · <Role>`, `Owner: <Role>`, then the headings Modules, Pseudocode (dated), Flowchart, Unit-test cases, Decisions. |
| `docs/design/lead.md` | 7 sections, 89 lines, about 2 rendered pages. |

**Entry dates (from git log):**
- L1.0 `89e87b6`, L1.1 `b45b529`, L1.6 `d1bcfe0`, L1.5 `ec6a8a6` and L1.7 `665a905` are all dated 2026-11-03.
- L1.2 `aa0b5ed`, L1.3 `cbecc3a` and L1.4 `7b0f111` are all dated 2026-11-09.

**Test runs:**
- `uv run pytest tests/unit -q` gives **106 passed**.
- `uv run pytest tests/unit tests/integration/test_phase1.py -q -rs` gives **112 passed, 14 skipped, 0 failed**. These are the same numbers as before this task, since only docs were added.

**Skips by owner.** Each skip is listed under the first stub it hits, found with a `--gate --tb=long` run:

| Owner | Count | Skipped tests |
| --- | --- | --- |
| Generator | 4 | all `generator_*` |
| Generator (first stub hit) | 2 | `matching_dfs_equals_nested_loops`, `e2e_pipeline_india_100` |
| Matching (`cycles.py:find_cycles`) | 5 | `matching_rings_on_fixtures`, the 2 heuristics tests, `simulation_failure_matches_analytic`, `e2e_solver_names_resolve` |
| Matching (`graph.py:nodes`) | 1 | `matching_graph_matches_edges` |
| Simulation | 2 | `metrics_on_fixture` (`compute_metrics`), `failure_p1_exact` (`FailureSimulator.__init__`) |

No skip belongs to the Lead.

## 3. Deviations from the request or the contract

1. **Branch.** The task said to create `p1/lead-docs`, but you then said to work on `p1/lead`. `p1/lead` had already been merged (PR #4), so I fast-forwarded it to `main` (`git merge --ff-only main`) and committed there. The new PR goes from `p1/lead` to `main` again.
2. **The report is in the same commit.** Step 6 came after step 5 in the task, but playbook section 3 says to commit the report with the work, so I wrote it first.
3. **No attribution lines.** CLAUDE.md overrides the tool's default co-author and "generated with" lines, so the commit and PR body have none.
4. **How "Corrected" is worded.** Reports 01–08 were written by the AI. They record deviations from the spec and choices you approved, not AI mistakes you caught. Each "Corrected" line says exactly what its report records, and none claims you caught an AI error. Add any real catches of your own (see next steps); graders weigh this field most.
5. **"Tool" and "Time" are `TODO (lead)` in all 8 entries.** No report states either of them.
6. **The template comment has a mode marker.** Its heading line ends in `· <mode>` (🧑‍🏫 / 🛠), because you asked for each entry to be marked. Otherwise it is the section-3 template unchanged.
7. **The ILP section is the plan, not code.** `solvers/ilp.py` is still a P2 stub, so section 1 of `lead.md` describes the formulation I will implement, and it says so. The other sections describe code that exists.
8. **No contract change. No teammate file edited.** The unstaged `team/01_lead.md` edit is still unstaged.

## 4. Things to note

1. **Heuristics has finished work that isn't merged.**
   - `origin/Heuristics_Branch` (`b47b852`, "first-come and greedy solvers with unit tests") has no PR yet.
   - Even once merged, its 2 integration tests stay skipped until `find_cycles` lands.
2. **Matching is the critical path.**
   - `find_cycles` is the first blocker for 4 tests outside Matching: 2 heuristics, 1 simulation and 1 e2e.
   - `CompatibilityGraph.__init__` is merged, but `nodes`, `successors`, `predecessors`, `has_edge`, `mutual_pairs` and `to_networkx` are still stubs.
3. **The P1 dates have passed.** Playbook section 1 put the P1 gate at Thu 5 Nov, and today is Mon 9 Nov. The phase-1 gate can't pass until Generator, Matching, Heuristics and Simulation merge. The schedule call is yours.
4. **The design-gate items are open.** No teammate has committed `docs/design/<role>.md` (playbook section 7, due 2 Nov). The empty headers now give them the place to do it.
5. **Mismatches.** `docs/design/lead.md` section 7 lists 6 places where the code and the playbook or Plan.md disagree. Two of them are worth a word to the team:
   - Plan.md says "five solvers", but there are seven.
   - The playbooks say `pool_8` was "solved by hand in week 1", but it was designed.
6. **The `MatchingSolver` default is still undecided** (reports 02 and 08). `team/03_matching.md` already expects `ValueError` at L=3, which argues for keeping the current behaviour and documenting it.

## 5. Next steps

- [ ] Run the `gh pr create` command from the chat answer, then merge once CI is green.
- [ ] Post the group-chat message from the chat answer.
- [ ] Fill in the 16 `TODO (lead)` fields in `ai_logs/lead.md`:
  - L1.0: Tool, Time
  - L1.1: Tool, Time
  - L1.5: Tool, Time
  - L1.6: Tool, Time
  - L1.7: Tool, Time
  - L1.2: Tool, Time
  - L1.3: Tool, Time
  - L1.4: Tool, Time
- [ ] Add to the "Corrected" lines anything you caught in the AI's output yourself. None of reports 01–08 records such a catch.
- [ ] Add an `ai_logs/lead.md` entry for this task (the docs and status update), if you want it logged. It was not in the requested list.
- [ ] Decide the `MatchingSolver` default (`lead.md` section 6.1). Then resolve or acknowledge the mismatches in section 7.
- [ ] Re-read `docs/design/lead.md` sections 1–2 for the viva. Rewrite section 1 against the real code once L2.1 lands.
